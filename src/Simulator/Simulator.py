from __future__ import annotations

import subprocess
import time
from copy import copy
from typing import Optional
from enum import Enum
import math
from pathlib import Path
from .ProcessContainer import ProcessContainer
from .ConfigurationHandler import ConfigurationHandler
from ..Utils import PATH_EXECUTABLE, ExperimentParameters, SimulationParameters, PATH_LOG_EXTRACTION_SCENE, PATH_CSV_REPLAY_SCENE, SimulationGapHandler, ExperimentMode, ExperimentType

import logging
logger = logging.getLogger("global_logger")


class Simulator:
    """
    TODO: rename to SimulatorHandler

    Controls the simulator. Can create and run instances of it in parallel to perform experiments.

    This is a singleton to ensure the simulator is only started from one source at a time.
    """

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
        """
        waits till all processes in the list are either ready or have timed out
        :param process_list:
        """
        while any([not p.ready for p in process_list]):
            for p_index, p in enumerate(process_list):
                if p.ready_timed_out(self._max_wait_for_ready):
                    process_list.pop(p_index)
                    p.terminate()
                    logger.warning("Process %s was terminated for not being ready after %s seconds", p.ep_index,
                                   self._max_wait_for_ready)
            time.sleep(self._max_wait_for_ready / 10)

    def _wait_for_spot(self, process_list : list[ProcessContainer]):
        """
        waits till one process in the list either finishes or times out
        :param process_list:
        :return:
        """
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
        """
        waits till all processes in the list are finished or timed out
        :param process_list:
        :return:
        """
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

    def run(self,
            scene_path : Path,
            experiment_parameters : list[ExperimentParameters],
            simulator_parameters : Optional[SimulationParameters]):
        """
        Runs the simulation for each of the experiment parameters. The simulator runs in parallel with _batch_size
        instances. Each instance waits up till _wait_for_ready seconds till timing out and for another _wait_for_finish
        seconds if the instance is ready.

        :param scene_path: The path to the scene file used.
        :param experiment_parameters: Data to perform each experiment
        :param simulator_parameters: Parameters of the simulator
        :return:
        """
        self._configurationHandler.reset_all()
        if simulator_parameters:
            self._configurationHandler.set_simulation_parameters(simulator_parameters)
        logger.info("Running %s experiments with a batch size of %s",len(experiment_parameters), self._batch_size)
        process_list : list[ProcessContainer] = []
        for ep_index, ep in enumerate(experiment_parameters):
            #wait for all processes to be ready
            self._wait_for_ready(process_list)
            #set parameters
            self._configurationHandler.set_experiment_parameters(ep)
            #wait for a space so that the number of active processes does not exceed the batch_size
            self._wait_for_spot(process_list)
            process_list.append(ProcessContainer(subprocess.Popen(str(PATH_EXECUTABLE) + " " + str(scene_path) + ".ros2",
                                         stdout=subprocess.PIPE, text=True), ep_index))
        #wait for all remaining processes to be ready
        self._wait_for_ready(process_list)
        self._configurationHandler.reset_all()
        self._wait_for_finished(process_list)

    def extract(self,
                data : Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]] = None,
                mode: ExperimentMode = ExperimentMode.PARTIAL):
        """
        Extracts the logs given in the data object from a .log into a .csv.

        :param data: which extractions should be performed.
            If data is None then all possible combinations are extracted.
            If a value in a tuple in data is None then it is replaced by a list of all possible values it could have.
        :param mode: either PARTIAL (only extract missing logs) or DELETE_EXISTING (delete existing extractions and
        re-extract all)
        """
        logger.info("Starting Log Extraction")
        # create eps
        eps = ExperimentParameters.create_experiment_parameters(None, data)
        # preprocessing
        if mode is ExperimentMode.DEL_EXISTING:
            for ep in eps:
                ep.delete_target()
        else:
            # remove eps that have an existing file
            eps = [ep for ep in eps if not ep.exists_extraction()]
        for ep in eps:
            ep.create_directories()
        # run
        if len(eps) > 0:
            try:
                self.run(PATH_LOG_EXTRACTION_SCENE, eps, None)
            except Exception as e:
                logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)
        logger.info("Finished Log Extraction")

    def replay(self,
               settings : SimulationParameters,
               data : Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]] = None,
               mode: ExperimentMode = ExperimentMode.PARTIAL):
        """
        Replay the given logs.

        :param settings: the used simulator settings
        :param data: which replays should be performed.
            If data is None then all possible combinations are replayed.
            If a value in a tuple in data is None then it is replaced by a list of all possible values it could have.
        :param mode: either PARTIAL (only replay missing logs) or DELETE_EXISTING (delete existing replay and
        re-replay all)
        """
        logger.info("Starting Log Replaying")
        # create eps
        eps = ExperimentParameters.create_experiment_parameters(settings.target_param_set_id, data)
        # preprocessing
        if mode is ExperimentMode.DEL_EXISTING:
            for ep in eps:
                ep.delete_target()
        else:
            eps = [ep for ep in eps if not ep.exists_replay()]
        for ep in eps:
            ep.create_directories()
        # run
        if len(eps) > 0:
            try:
                self.run(PATH_CSV_REPLAY_SCENE, eps, settings)
            except Exception as e:
                logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)
        logger.info("Finished Log Replay")

    def simulation_gap(self,
                       settings : SimulationParameters,
                       data : Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]] = None,
                       extraction_mode : ExperimentMode = ExperimentMode.PARTIAL,
                       replay_mode : ExperimentMode = ExperimentMode.PARTIAL)\
            -> SimulationGapHandler:
        """
        Create simulation gap objects for the given experiments. Automatically extracts and replays logs as necessary.

        :param settings: the settings of the simulator
        :param data: logs for which a simulation gap object should be created
            If data is None then all possible combinations are replayed.
            If a value in a tuple in data is None then it is replaced by a list of all possible values it could have.
        :param extraction_mode: either PARTIAL (only extract missing logs) or DELETE_EXISTING (delete existing extractions and
        re-extract all)
        :param replay_mode: either PARTIAL (only replay missing logs) or DELETE_EXISTING (delete existing replay and
        re-replay all)
        :return: a list of SimulationGap objects
        """
        self.extract(data, extraction_mode)
        self.replay(settings, data, replay_mode)
        eps = ExperimentParameters.create_experiment_parameters(settings.target_param_set_id, data)
        gap_handler = SimulationGapHandler(settings.target_param_set_id)
        for ep in eps:
            gap_handler.add(ep.action_name, ep.recording_date, ep.log_index)
        return gap_handler

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