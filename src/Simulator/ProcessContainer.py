import subprocess
import time
from enum import Enum

import logging
logger = logging.getLogger("global_logger")
class ProcessContainer:
    """
    Used in the Simulator class to represent an instance of the running simulator.
    """

    def __init__(self, process: subprocess.Popen[str], ep_index):
        self._p: subprocess.Popen[str] = process
        self._ep_index: int = ep_index
        self._start_time = time.time()
        self._ready_time = 0
        self._terminated = False

    def update_ready(self):
        if self.ready:
            return
        for line in self._p.stdout:
            if line.strip() == "READY":
                self._ready_time = time.time()
                logger.info("Process %s is ready", self._ep_index)


    def update_status(self, max_wait_for_ready: float, max_wait_for_finish: float) -> bool:
        if self._ready_time > 0:
            # process was ready and has been running for some time
            # check successful termination
            if self._p.poll() is not None:
                logger.info("Process %s finished", self._ep_index)
                return True
            # check timeout
            elif time.time() - self._start_time > max_wait_for_ready:
                logger.warning("Process %s was terminated for not being ready after %s seconds", self._ep_index,
                               max_wait_for_ready)
                return True
            #process is neither finished nor timed out, wait for next update
            return False
        # process is not yet ready
        if time.time() - self._ready_time > max_wait_for_ready:

            return True
        # check if process is now ready
        else:
            for line in self._p.stdout:
                if line.strip() == "READY":
                    self._ready_time = time.time()
                    logger.info("Process %s is ready", self._ep_index)
                    return False
            return False

    def ready_timed_out(self, max_wait_for_ready : float) -> bool:
        if self._ready_time > 0:
            return False
        return (time.time() - self._ready_time) > max_wait_for_ready

    def finished_timed_out(self, max_wait_for_finish : float) -> bool:
        if self._ready_time > 0:
            return (time.time() - self._start_time) > max_wait_for_finish
        return False

    @property
    def ready(self) -> bool:
        if self._ready_time > 0:
            return True
        for line in self._p.stdout:
            if line.strip() == "READY":
                self._ready_time = time.time()
                logger.info("Process %s is ready", self._ep_index)
                return True
        return False

    @property
    def finished(self) -> bool:
        return self._p.poll() is not None

    @property
    def ep_index(self) -> int:
        return self._ep_index

    def terminate(self):
        self._p.terminate()
