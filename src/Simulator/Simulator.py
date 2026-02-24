from __future__ import annotations

import subprocess
import time
from typing import Optional
from enum import Enum
import math
from pathlib import Path
from .ProcessContainer import ProcessContainer
from .ConfigurationHandler import ConfigurationHandler
from ..Utils import PATH_EXECUTABLE, ExperimentParameters, SimulationParameters, PATH_LOG_EXTRACTION_SCENE, PATH_CSV_REPLAY_SCENE, SimulationGapData, ExperimentMode

import logging
logger = logging.getLogger("global_logger")


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
        self._max_wait_for_finish = 20
        self._show_ui = True #TODO


    def _wait_for_ready(self, process_list : list[ProcessContainer]):
        while any([not p.ready for p in process_list]):
            for p_index, p in enumerate(process_list):
                if p.ready_timed_out(self._max_wait_for_ready):
                    process_list.pop(p_index)
                    p.terminate()
                    logger.warning("Process %s was terminated for not being ready after %s seconds", p.ep_index,
                                   self._max_wait_for_ready)
            time.sleep(self._max_wait_for_ready / 10)

    def _wait_for_spot(self, process_list : list[ProcessContainer]):
        while len(process_list) >= self._batch_size:
            for p_index, p in enumerate(process_list):
                if p.finished:
                    logger.info("Process %s finished", p.ep_index)
                    process_list.pop(p_index)
                elif p.finished_timed_out(self._max_wait_for_finish):
                    logger.info("Process %s was terminated after not finishing in %s", p.ep_index,
                                self._max_wait_for_finish)
                    process_list.pop(p_index)
                    p.terminate()
            time.sleep(self._max_wait_for_ready / 10)

    def _wait_for_finished(self, process_list : list[ProcessContainer]):
        while len(process_list) > 0:
            for p_index, p  in enumerate(process_list):
                if p.finished:
                    logger.info("Process %s finished", p.ep_index)
                    process_list.pop(p_index)
                elif p.finished_timed_out(self._max_wait_for_finish):
                    logger.info("Process %s was terminated after not finishing in %s", p.ep_index,
                                self._max_wait_for_finish)
                    process_list.pop(p_index)
                    p.terminate()
            time.sleep(self._max_wait_for_ready / 10)

    def run(self, scene_path : Path, experiment_parameters : list[ExperimentParameters], simulator_parameters : Optional[SimulationParameters]):
        self._configurationHandler.reset_all()
        if simulator_parameters:
            self._configurationHandler.set_simulation_parameters(simulator_parameters)
        logger.info("Running %s experiments with a batch size of %s",len(experiment_parameters), self._batch_size)
        process_list : list[ProcessContainer] = []
        for ep_index, ep in enumerate(experiment_parameters):
            for _ in range(ep.num_missing_copies):
                #wait for all processes to be ready
                self._wait_for_ready(process_list)
                #set parameters
                if not self._configurationHandler.set_experiment_parameters(ep):
                    logger.warning("Experiment %s was skipped due to inconsistent experiment_parameter %s", ep_index, ep)
                    continue
                #wait for a space so that the number of active processes does not exceed the batch_size
                self._wait_for_spot(process_list)
                process_list.append(ProcessContainer(subprocess.Popen(str(PATH_EXECUTABLE) + " " + str(scene_path) + ".ros2",
                                             stdout=subprocess.PIPE, text=True), ep_index))
        #wait for all remaining processes to be ready
        self._wait_for_ready(process_list)
        self._configurationHandler.reset_all()
        self._wait_for_finished(process_list)

    def extract(self, action_names: Optional[list[str]] = None,
                recording_dates: Optional[list[str]] = None, log_indices: Optional[list[int]] = None, mode: ExperimentMode = ExperimentMode.PARTIAL):
        logger.info("Extracting logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        eps = ExperimentParameters.get_extraction_data(action_names, recording_dates, log_indices, mode)
        self.extract_ep(eps)

    def extract_ep(self, eps : list[ExperimentParameters]):
        try:
            self.run(PATH_LOG_EXTRACTION_SCENE, eps, None)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)

    def replay(self, settings : SimulationParameters, action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None,
               log_indices : Optional[list[int]] = None, mode: ExperimentMode = ExperimentMode.PARTIAL, num_copies : int = 1):
        if num_copies < 0:
            return
        logger.info("Replaying logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        eps = ExperimentParameters.get_replay_data(settings.target_param_set_id, action_names, recording_dates, log_indices, num_copies, mode)
        self.replay_ep(settings, eps)

    def replay_ep(self, settings : SimulationParameters, eps : list[ExperimentParameters]):
        try:
            self.run(PATH_CSV_REPLAY_SCENE, eps, settings)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)

    def simulation_gap(self, settings : SimulationParameters,
                       action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None, log_indices : Optional[list[int]] = None,
                       mode: ExperimentMode = ExperimentMode.PARTIAL, num_replays : int = 1) -> list[SimulationGapData]:

        pass


    @property
    def batch_size(self) -> int:
        return self._batch_size

    @property
    def max_wait_for_ready(self) -> float:
        return self._max_wait_for_ready

    @property
    def max_run_duration(self) -> float:
        return self._max_wait_for_finish

    @property
    def show_ui(self) -> bool:
        return self._show_ui

    @batch_size.setter
    def batch_size(self, value):
        if value > self._MAX_INSTANCES:
            logger.warning("Given batch_size (%s) was larger than the allowed maximum (%s). The value will set to the allowed maximum",
                           value, self._MAX_INSTANCES)
            self._batch_size = self._MAX_INSTANCES
        elif value < 1:
            logger.warning("Given batch_size (%s) was smaller than 1. The value will be set to 1",
                           self._batch_size)
            self._batch_size = 1
        else:
            self._batch_size = value

    @max_wait_for_ready.setter
    def max_wait_for_ready(self, value):
        if value < 0:
            logger.warning(
                "max_ready_for_wait (%s) cannot be negative. The value will be set to 0",
                value)
            self._max_wait_for_ready = 0
        else:
            self._max_wait_for_ready = value

    @max_run_duration.setter
    def max_run_duration(self, value):
        if value < 0:
            logger.warning(
                "max_run_duration (%s) cannot be negative. The value will be set to 0",
                value)
            self._max_wait_for_finish = 0
        else:
            self._max_wait_for_finish = value

    @show_ui.setter
    def show_ui(self, value):
        self._show_ui = value