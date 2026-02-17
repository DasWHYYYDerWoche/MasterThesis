from __future__ import annotations

import subprocess
import time
from typing import Optional
from enum import Enum
import math
from pathlib import Path
from datetime import datetime

from .SimulatorSettings import SimulatorSettings
from .ConfigurationHandler import LoggerCfgHandler, NaoV6H25Handler, ThesisCSVReplayHandler, ThesisLogExtractionHandler
from ..Utils import PATH_EXECUTABLE, ExperimentData, ExperimentType, PATH_LOG_EXTRACTION_SCENE, PATH_CSV_REPLAY_SCENE

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
        self._param_set_id = ""
        if self._initialized:
            return
        self._initialized = True
        self._MAX_INSTANCES = 5
        self._loggerCfgHandler = LoggerCfgHandler()
        self._naoV6H25Handler = NaoV6H25Handler()
        self._thesisCSVReplayHandler = ThesisCSVReplayHandler()
        self._thesisLogExtractionHandler = ThesisLogExtractionHandler()

    def _set_simulator_settings(self, settings : SimulatorSettings):
        self._thesisCSVReplayHandler.set( settings.kd, settings.kp, settings.contact_kd, settings.contact_kp)
        """
        if settings.kd:
            self._thesisCSVReplayHandler.kd = settings.kd
        if settings.kp:
            self._thesisCSVReplayHandler.kp = settings.kp
        if settings.contact_kd:
            self._thesisCSVReplayHandler.contact_kd = settings.contact_kd
        if settings.contact_kp:
            self._thesisCSVReplayHandler.contact_kp = settings.contact_kp
        """
        self._thesisCSVReplayHandler.write_to_file()
        for hinge_name, hinge in settings.hinge_parameters.items():
            self._naoV6H25Handler.set_hinge_parameters(hinge_name, hinge)
        self._naoV6H25Handler.write_to_file()

    def _set_experiment_parameters(self, experiment_data : ExperimentData) -> bool:
        if experiment_data.experiment_type is ExperimentType.LOG_EXTRACTION:
            self._loggerCfgHandler.set_extract(experiment_data.log_extraction_path_relative.as_posix())
            self._loggerCfgHandler.write_to_file()
            self._thesisLogExtractionHandler.set(experiment_data.log_path.as_posix())
            self._thesisLogExtractionHandler.write_to_file()
            return True
        elif experiment_data.experiment_type is ExperimentType.CSV_REPLAY:
            self._loggerCfgHandler.set_replay(experiment_data.log_extraction_path_relative.as_posix(), experiment_data.csv_replay_path_relative.as_posix())
            self._loggerCfgHandler.write_to_file()
            self._thesisLogExtractionHandler.set_default()
            self._thesisLogExtractionHandler.write_to_file()
            return True
        else:
            return False

    def _reset_simulator(self):
        self._loggerCfgHandler.set_default()
        self._loggerCfgHandler.write_to_file()
        self._thesisCSVReplayHandler.set_default()
        self._thesisCSVReplayHandler.write_to_file()
        self._naoV6H25Handler.set_default()
        self._naoV6H25Handler.write_to_file()
        self._thesisLogExtractionHandler.set_default()
        self._thesisLogExtractionHandler.write_to_file()

    def run(self, scene_path : Path, experiment_datas : list[ExperimentData], batch_size : int, max_wait_for_ready : float = 10, max_run_duration : float = 20, gui : bool = True):
        if max_wait_for_ready < 0 or max_run_duration < 0:
            logger.error("max_ready_for_wait (%s) and max_run_duration (%s) have to be greater than 0", max_wait_for_ready, max_run_duration)
            return
        if batch_size > self._MAX_INSTANCES:
            logger.warning("batch_size (%s) was larger than the maximum number of allowed instances (%s)", batch_size, self._MAX_INSTANCES)
            batch_size = self._MAX_INSTANCES
        logger.info("Extracting %s logs with a batch size of %s",len(experiment_datas), batch_size)
        for i in range(0, math.ceil(len(experiment_datas) / batch_size) * batch_size, batch_size):
            self._run_batch(scene_path, experiment_datas[i : min(i+batch_size, len(experiment_datas))])

    def _run_batch(self,  scene_path : Path, experiment_datas : list[ExperimentData], max_wait_for_ready : float = 10, max_run_duration : float = 20, gui : bool = True):
        process_list: list[subprocess.Popen[str]] = []
        process_start_time: list[float] = [0 for _ in experiment_datas]
        process_ready_time: list[float] = [0 for _ in experiment_datas]
        logger.debug("Staring new batch")
        try:
            for i in range(len(experiment_datas)):
                if not self._set_experiment_parameters(experiment_datas[i]):
                    logger.warning("Experiment %s was skipped due to inconsistent experiment_data %s", i, experiment_datas[i])
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
                    if time.time() - process_start_time[i] > max_wait_for_ready:
                        process_list[i].terminate()
                        logger.warning("Process %s was terminated for not being ready after %s seconds", i,
                                       max_wait_for_ready)
                        break
            # wait for processes to finish
            any_running = True
            while any_running:
                for i in range(len(process_list)):
                    if process_list[i].poll() is None:
                        if time.time() - process_ready_time[i] > max_run_duration:
                            process_list[i].terminate()
                            logger.warning("Process %s was terminated for not being finished after %s seconds", i,
                                           max_wait_for_ready)
                any_running = any([True if process.poll() is None else False for process in process_list])
                time.sleep(max_run_duration / 20)
        except Exception as e:
            logger.exception("Exception %s occurred during log extraction. Argument list:\n %s, %s, %s, %s",
                             type(e).__name__, experiment_datas, max_wait_for_ready, max_run_duration, gui)

    def extract(self, action_names: Optional[list[str]] = None,
                recording_dates: Optional[list[str]] = None, log_indices: Optional[list[int]] = None, mode: ExperimentMode = ExperimentMode.PARTIAL, batch_size: int = 5, ):
        """

        :param action_names:
        :param recording_dates:
        :param log_indices:
        :param mode: FULL: extract all given logs, PARTIAL: extract only logs without csv, DEL_EXISTING: delete existing csv of given logs and reextract all
        :param batch_size:
        :return:
        """
        logger.info("Extracting logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)

        eds = ExperimentData.get_extraction_data(action_names, recording_dates, log_indices)
        if mode == ExperimentMode.PARTIAL:
            eds = ExperimentData.delete_redundant_eds(eds)
        elif mode == ExperimentMode.DEL_EXISTING:
            ExperimentData.delete_existing_csvs(eds)
        ExperimentData.create_directories(eds)
        try:
            self.run(PATH_LOG_EXTRACTION_SCENE, eds, batch_size)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)
        self._reset_simulator()

    def replay(self, settings : SimulatorSettings, action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None, log_indices : Optional[list[int]] = None, mode: ExperimentMode = ExperimentMode.PARTIAL, batch_size : int = 5, num_copies : int = 1):
        """

        :param settings:
        :param action_names:
        :param recording_dates:
        :param log_indices:
        :param mode: FULL: extract all given logs, PARTIAL: extract only logs with missing csvs, DEL_EXISTING: delete existing csv of given logs and reextract all
        :param batch_size:
        :param num_copies:
        :return:
        """
        if num_copies < 0:
            return
        logger.info("Replaying logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        if settings:
            self._set_simulator_settings(settings)
        eds = ExperimentData.get_replay_data(settings.target_param_set_id, action_names, recording_dates, log_indices, num_copies)
        if mode == ExperimentMode.PARTIAL:
            eds = ExperimentData.delete_redundant_eds(eds)
        elif mode == ExperimentMode.DEL_EXISTING:
            ExperimentData.delete_existing_csvs(eds)
        ExperimentData.create_directories(eds)
        try:
            for _ in range(num_copies):
                self.run(PATH_CSV_REPLAY_SCENE, eds, batch_size)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)
        self._reset_simulator()