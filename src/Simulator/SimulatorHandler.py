from __future__ import annotations

import subprocess
import time
from typing import Optional, Any
from pathlib import Path
from .ProcessContainer import ProcessContainer
from .ConfigurationHandler import ConfigurationHandler
from ..Constants import PATH_EXECUTABLE, PATH_LOG_EXTRACTION_SCENE, PATH_CSV_REPLAY_SCENE, PATH_LOGS
from ..Utils import ExperimentParameters , SimulationGapHandler, ExperimentMode, SimulationParameters, sim_params_from_file

import logging
logger = logging.getLogger("global_logger")


class SimulatorHandler:
    """
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
        self._MAX_INSTANCES = 30

        self._num_instances = 2
        self._replays_per_instance = 2

        self._max_wait_for_ready = 5
        self._max_wait_for_finish = 10

        self._dt = -1
        self._show_ui = True


    def _wait_for_ready(self, process_list : list[ProcessContainer]):
        """
        waits till all processes in the list are either ready or have timed out
        :param process_list:
        """
        while any([not p.ready for p in process_list]):
            # there are still processes that are not ready, check if any timed out
            for p_index, p in enumerate(process_list):
                if p.ready_timed_out(self._max_wait_for_ready):
                    process_list.pop(p_index)
                    p.terminate()
                    logger.warning("Process %s was terminated for not being ready after %s seconds", p.ep_index,
                                   self._max_wait_for_ready)
            time.sleep(0.001)

    def _check_finished(self, process_list : list[ProcessContainer]):
        """
        waits till one process in the list either finishes or times out
        :param process_list:
        :return:
        """
        for p_index, p in enumerate(process_list):
            if p.finished:
                logger.debug("Process %s finished", p.ep_index)
                process_list.pop(p_index)
            elif p.finished_timed_out(self._max_wait_for_finish):
                logger.warning("Process %s was terminated after not finishing in %s", p.ep_index,
                               self._max_wait_for_finish)
                process_list.pop(p_index)
                p.terminate()

    def _wait_for_spot(self, process_list : list[ProcessContainer]):
        """
        waits till one process in the list either finishes or times out
        :param process_list:
        :return:
        """
        while len(process_list) >= self._num_instances:
            self._check_finished(process_list)
            time.sleep(0.001)

    def _wait_for_finished(self, process_list : list[ProcessContainer]):
        """
        waits till all processes in the list are finished or timed out
        :param process_list:
        :return:
        """
        while len(process_list) > 0:
            self._check_finished(process_list)
            time.sleep(0.001)

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
            self._configurationHandler.set_simulation_parameters(simulator_parameters, self._dt)
            logger.info("Replaying %s experiments with %d parallel instances and %d replays per instance", len(experiment_parameters),
                        self._num_instances, self._replays_per_instance)
        else:
            logger.info("Extracting %s experiments with %d parallel instances.", len(experiment_parameters), self._num_instances)
        process_list : list[ProcessContainer] = []
        ep_index = 0
        process_index = 0
        while ep_index < len(experiment_parameters):
            ep = experiment_parameters[ep_index]
            #wait for all processes to be ready
            self._wait_for_ready(process_list)
            #set parameters
            if simulator_parameters:
                new_ep_index = min(ep_index + self._replays_per_instance, len(experiment_parameters))
                self._configurationHandler.set_replay_parameters(experiment_parameters[ep_index:new_ep_index])
            else:
                self._configurationHandler.set_extraction_parameters(ep)
                new_ep_index = ep_index + 1
            self._check_finished(process_list)
            #wait for a space so that the number of active processes does not exceed the batch_size
            self._wait_for_spot(process_list)
            p_open_str = str(PATH_EXECUTABLE) + " " + str(scene_path) + ".ros2"
            if not self.show_ui:
                p_open_str = p_open_str + " -platform offscreen"
            logger.debug("Process %d created with eps %d to %d", process_index, ep_index, new_ep_index - 1)
            process_list.append(ProcessContainer(subprocess.Popen(p_open_str, stdout=subprocess.PIPE, text=True), process_index))
            ep_index = new_ep_index
            process_index += 1
        #wait for all remaining processes to be ready
        self._wait_for_ready(process_list)
        self._configurationHandler.reset_all()
        self._wait_for_finished(process_list)
        if simulator_parameters:
            logger.info("Finished replaying.")
        else:
            logger.info("Finished extraction.")


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

    def get_parameter_value(self, parameter_name) -> Any:
        return self._configurationHandler.get_parameter_value(parameter_name)

    def get_default_value(self, parameter_name) -> Any:
        return self._configurationHandler.get_default_value(parameter_name)

    def set_configurations(self, eps : list[ExperimentParameters], sim_params : Optional[SimulationParameters] = None):
        if sim_params is not None:
            self._configurationHandler.set_replay_parameters(eps)
            self._configurationHandler.set_simulation_parameters(sim_params, self._dt)
        else:
            self._configurationHandler.set_extraction_parameters(eps[0])

    def set_configurations_from_file(self,
                                     action : str,
                                     recording_date : str,
                                     log_index : int,
                                     path : Optional[Path] = None,
                                     sim_params_index : Optional[int] = None):
        sim_params = sim_params_from_file(path, sim_params_index)
        ep = ExperimentParameters(sim_params.target_param_set_id, action, recording_date, log_index)
        self.set_configurations([ep], sim_params)

    @property
    def num_instances(self) -> int:
        return self._num_instances

    @property
    def replays_per_instance(self) -> int:
        return self._replays_per_instance

    @property
    def max_wait_for_ready(self) -> float:
        return self._max_wait_for_ready

    @property
    def max_run_duration(self) -> float:
        return self._max_wait_for_finish

    @property
    def show_ui(self) -> bool:
        return self._show_ui

    @property
    def dt(self) -> int:
        return self._dt

    @num_instances.setter
    def num_instances(self, value):
        if value > self._MAX_INSTANCES:
            logger.warning("Given batch_size (%s) was larger than the allowed maximum (%s). The value will set to the allowed maximum",
                           value, self._MAX_INSTANCES)
            self._num_instances = self._MAX_INSTANCES
        elif value < 1:
            logger.warning("Given batch_size (%s) was smaller than 1. The value will be set to 1",
                           self._num_instances)
            self._num_instances = 1
        else:
            self._num_instances = value

    @replays_per_instance.setter
    def replays_per_instance(self, value):
        self._replays_per_instance = value

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

    @dt.setter
    def dt(self, value):
        self._dt = value


# emergency methods
    def split_logs(self):
        nao = "Jarvis"
        path = PATH_LOGS / "ThesisFullLogs"
        log_path = path / nao
        split_command_file = (path / "extractionJarvis").with_suffix(".txt")
        d = {}
        cur_file = ""
        with open(split_command_file) as f:
            f_iter = iter(f)
            line = next(f_iter,None).strip()
            while line is not None:
                line = line.strip()
                if line.endswith(".log"):
                    cur_file = line
                    d[cur_file] = []
                elif line.startswith("log"):
                    first_line = line
                    line = next(f_iter, None)
                    second_line = line.strip()
                    d[cur_file].append((first_line,second_line))
                line = next(f_iter, None)
        for file, commands in d.items():
            relative_path = (Path("..") / "Logs" / "ThesisFullLogs" / nao / file).as_posix()
            for first_line, second_line in commands:
                self._configurationHandler._loggerCfgHandler.set(logging_mode=2,
                                                                 log_extraction_path="\"" + first_line + "\"",
                                                                 csv_replay_path="\"" + second_line + "\"",
                                                                 move_robot=0,
                                                                 recording_duration=0)
                self._configurationHandler._loggerCfgHandler.write_to_file()
                self._configurationHandler._thesisLogExtractionHandler.set(relative_path)
                self._configurationHandler._thesisLogExtractionHandler.write_to_file()
                p_open_str = str(PATH_EXECUTABLE) + " " + str(PATH_LOG_EXTRACTION_SCENE) + ".ros2"
                #if not self.show_ui:
                 #   p_open_str = p_open_str + " -platform offscreen"
                p = subprocess.Popen(p_open_str, stdout=subprocess.PIPE, text=True)
                timer = 0
                time.sleep(5)
                p.terminate()

