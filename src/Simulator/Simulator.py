from __future__ import annotations

import subprocess
import time
from typing import Optional
from enum import Enum
import math
from pathlib import Path
from .ConfigurationHandler import ConfigurationHandler
from ..Utils import PATH_EXECUTABLE, ExperimentParameters, SimulationParameters, PATH_LOG_EXTRACTION_SCENE, PATH_CSV_REPLAY_SCENE

import logging
logger = logging.getLogger("global_logger")

class ExperimentMode(Enum):
    FULL = 0
    PARTIAL = 1
    DEL_EXISTING = 2

class Simulator:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._configurationHandler = ConfigurationHandler()
        self._MAX_INSTANCES = 5

        self._batch_size = 2
        self._max_wait_for_ready = 10
        self._show_ui = True #TODO

    def run(self, scene_path : Path, experiment_parameters : list[ExperimentParameters], max_run_duration : float = 20):
        if max_run_duration < 0:
            logger.error("max_ready_for_wait (%s) and max_run_duration (%s) have to be greater than 0", self._max_wait_for_ready, max_run_duration)
            return
        logger.info("Running %s experiments with a batch size of %s",len(experiment_parameters), self._batch_size)
        for i in range(0, math.ceil(len(experiment_parameters) / self._batch_size) * self._batch_size, self._batch_size):
            self._run_batch(scene_path, experiment_parameters[i : min(i+self._batch_size, len(experiment_parameters))])

    def _run_batch(self, scene_path : Path, experiment_parameters : list[ExperimentParameters], max_run_duration : float = 20):
        process_list: list[subprocess.Popen[str]] = []
        process_start_time: list[float] = [0 for _ in experiment_parameters]
        process_ready_time: list[float] = [0 for _ in experiment_parameters]
        logger.debug("Staring new batch")
        try:
            for i in range(len(experiment_parameters)):
                if not self._configurationHandler.set_experiment_parameters(experiment_parameters[i]):
                    logger.warning("Experiment %s was skipped due to inconsistent experiment_parameter %s", i, experiment_parameters[i])
                    continue
                process_list.append(
                    subprocess.Popen(str(PATH_EXECUTABLE) + " " + str(scene_path) + ".ros2",
                                     stdout=subprocess.PIPE, text=True))
                process_start_time[i] = time.time()
                # wait for process to have started (and loaded all parameters from logs) before updating parameters for next process
                for line in process_list[i].stdout:
                    if line.strip() == "READY":
                        process_ready_time[i] = time.time()
                        logger.debug("Process %s is ready", i)
                        break
                    if time.time() - process_start_time[i] > self._max_wait_for_ready:
                        process_list[i].terminate()
                        logger.warning("Process %s was terminated for not being ready after %s seconds", i,
                                       self._max_wait_for_ready)
                        break
            # wait for processes to finish
            any_running = True
            while any_running:
                for i in range(len(process_list)):
                    if process_list[i].poll() is None:
                        if time.time() - process_ready_time[i] > max_run_duration:
                            process_list[i].terminate()
                            logger.warning("Process %s was terminated for not being finished after %s seconds", i,
                                           self._max_wait_for_ready)
                any_running = any([True if process.poll() is None else False for process in process_list])
                time.sleep(max_run_duration / 20)
        except Exception as e:
            logger.exception("Exception %s occurred during log extraction. Argument list:\n %s, %s, %s, %s",
                             type(e).__name__, experiment_parameters, self._max_wait_for_ready, max_run_duration)

    def extract(self, action_names: Optional[list[str]] = None,
                recording_dates: Optional[list[str]] = None, log_indices: Optional[list[int]] = None, mode: ExperimentMode = ExperimentMode.PARTIAL):
        """

        :param action_names:
        :param recording_dates:
        :param log_indices:
        :param mode: FULL: extract all given logs, PARTIAL: extract only logs without csv, DEL_EXISTING: delete existing csv of given logs and reextract all
        :return:
        """
        logger.info("Extracting logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        eps = ExperimentParameters.get_extraction_data(action_names, recording_dates, log_indices)
        if mode == ExperimentMode.PARTIAL:
            eps = ExperimentParameters.delete_redundant_eps(eps)
        elif mode == ExperimentMode.DEL_EXISTING:
            ExperimentParameters.delete_existing_csvs(eps)
        ExperimentParameters.create_directories(eps)
        self._configurationHandler.reset_all()
        try:
            self.run(PATH_LOG_EXTRACTION_SCENE, eps)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)
        self._configurationHandler.reset_all()

    def replay(self, settings : SimulationParameters, action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None, log_indices : Optional[list[int]] = None, mode: ExperimentMode = ExperimentMode.PARTIAL, num_copies : int = 1):
        """

        :param settings:
        :param action_names:
        :param recording_dates:
        :param log_indices:
        :param mode: FULL: extract all given logs, PARTIAL: extract only logs with missing csvs, DEL_EXISTING: delete existing csv of given logs and reextract all
        :param num_copies:
        :return:
        """
        if num_copies < 0:
            return
        logger.info("Replaying logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        self._configurationHandler.reset_all()
        if settings:
            self._configurationHandler.set_simulation_parameters(settings)
        eps = ExperimentParameters.get_replay_data(settings.target_param_set_id, action_names, recording_dates, log_indices, num_copies)
        if mode == ExperimentMode.PARTIAL:
            eps = ExperimentParameters.delete_redundant_eps(eps)
        elif mode == ExperimentMode.DEL_EXISTING:
            ExperimentParameters.delete_existing_csvs(eps)
        ExperimentParameters.create_directories(eps)
        eps = ExperimentParameters.split_eps(eps)
        try:
            self.run(PATH_CSV_REPLAY_SCENE, eps)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)
        self._configurationHandler.reset_all()

    def simulation_gap(self, settings : SimulationParameters, action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None, log_indices : Optional[list[int]] = None, mode: ExperimentMode = ExperimentMode.PARTIAL, num_copies : int = 1):
        pass


    @property
    def batch_size(self) -> int:
        return self._batch_size

    @property
    def max_wait_for_ready(self) -> float:
        return self._max_wait_for_ready

    @property
    def show_ui(self) -> bool:
        return self._show_ui

    @batch_size.setter
    def batch_size(self, value):
        if value > self._MAX_INSTANCES:
            logger.warning("given batch_size (%s) was larger than the maximum number of allowed instances (%s)", self._batch_size, self._MAX_INSTANCES)
            self._batch_size = self._MAX_INSTANCES
        else:
            self._batch_size = value

    @max_wait_for_ready.setter
    def max_wait_for_ready(self, value):
        self._max_wait_for_ready = value

    @show_ui.setter
    def show_ui(self, value):
        self._show_ui = value