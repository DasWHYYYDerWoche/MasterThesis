from __future__ import annotations

import subprocess
import time
from typing import Optional

from .FileHandler import LoggerHandler, NaoV6H25Handler, ThesisCSVReplayHandler, ThesisLogExtractionHandler
from ..Utils import PATH_LOG_EXTRACTION_SCENE, PATH_EXECUTABLE, ExtractionData

import logging
logger = logging.getLogger("global_logger")

class Simulator:
    _instance = None
    _initialized = False

    def __init__(self):
        if self._initialized:
            return

        self.MAX_INSTANCES = 5
        self._loggerHandler = LoggerHandler()
        self._naoV6H25Handler = NaoV6H25Handler()
        self._thesisCSVReplayHandler = ThesisCSVReplayHandler()
        self._thesisLogExtractionHandler = ThesisLogExtractionHandler()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def _set_log_extraction_parameters(self, extraction_data : ExtractionData):
        self._loggerHandler.set(logging=True, log_extraction=True, csv_replay=False,
                                action_name=extraction_data.action_name, log_folder=extraction_data.date,
                                log_index=extraction_data.log_index,
                                csv_name="")
        self._loggerHandler.write_to_file()
        relative_path = ".." + "/Logs/ThesisFieldLogs/" + extraction_data.action_name + "/" + extraction_data.date + "/" + (str(extraction_data.log_index) + ".log")
        self._thesisLogExtractionHandler.set(relative_path)
        self._thesisLogExtractionHandler.write_to_file()

    def _reset_log_extraction_parameters(self):
        self._loggerHandler.set_default()
        self._loggerHandler.write_to_file()
        self._thesisLogExtractionHandler.set_default()
        self._thesisLogExtractionHandler.write_to_file()

    def run_log_extraction(self, extraction_datas : list[ExtractionData], max_wait_for_ready : float = 10, max_run_duration : float = 20, gui : bool = True):

        if len(extraction_datas) > self.MAX_INSTANCES:
            return False
        if max_wait_for_ready < 0 or max_run_duration < 0:
            return False
        process_list : list[subprocess.Popen[str]] = []
        process_start_time : list[float] = [0 for _ in extraction_datas]
        process_ready_time : list[float] = [0 for _ in extraction_datas]
        logger.info("Running log extraction with %s instances",len(extraction_datas))
        try:
            for i in range(len(extraction_datas)):
                self._set_log_extraction_parameters(extraction_datas[i])
                process_list.append(subprocess.Popen(str(PATH_EXECUTABLE) + " " + str(PATH_LOG_EXTRACTION_SCENE) + ".ros2",
                                 stdout=subprocess.PIPE, text=True))
                process_start_time[i] = time.time()
                #wait for process to have started (and loaded all parameters from logs) before updating parameters for next process
                for line in process_list[i].stdout:
                    if line.strip() == "READY":
                        process_ready_time[i] = time.time()
                        logger.debug("Process %s is ready", i)
                        break
                    if time.time() - process_start_time[i] > max_wait_for_ready:
                        process_list[i].terminate()
                        logger.warning("Process %s was terminated for not being ready after %s seconds", i, max_wait_for_ready)
                        break
            self._reset_log_extraction_parameters()
            #wait for processes to finish
            any_running = True
            while any_running:
                for i in range(len(process_list)):
                    if process_list[i].poll() is None:
                        if time.time() - process_ready_time[i] > max_run_duration:
                            process_list[i].terminate()
                            logger.warning("Process %s was terminated for not being finished after %s seconds", i, max_wait_for_ready)
                any_running = any([True if process.poll() is None else False for process in process_list])
                time.sleep(max_run_duration / 20)
        except Exception as e:
            logger.exception("Exception %s occurred during log extraction. Argument list:\n %s, %s, %s, %s", type(e).__name__, extraction_datas, max_wait_for_ready, max_run_duration, gui)

    def _set_csv_replay_parameters(self):
        pass

    def _reset_csv_replay_parameters(self):
        self._loggerHandler.set_default()
        self._loggerHandler.write_to_file()

instance : Optional[Simulator] = None