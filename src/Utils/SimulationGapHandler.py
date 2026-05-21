from __future__ import annotations
from itertools import zip_longest
import numpy as np
import pandas
from typing import Optional, Callable, TypeVar

from .SimulationGapData import SimulationGapData
from ..Constants import get_project_root

import logging
logger = logging.getLogger("global_logger")

T = TypeVar("T")

class SimulationGapHandler:
    def __init__(self, param_set_id: str):
        self._sim_gap_data : dict[str, list[SimulationGapData]] = {}
        self._param_set_id: str = param_set_id
        path = get_project_root() / "executables/statistics/statistics.csv"
        df = pandas.read_csv(path)[["statistic", "max"]]
        self._max_pos = df.loc[df["statistic"] == "max_pos_abs", "max"].iloc[0]
        self._max_vel = df.loc[df["statistic"] == "max_vel_abs", "max"].iloc[0]
        self._max_acc = df.loc[df["statistic"] == "max_acc_abs", "max"].iloc[0]
        self._num_loaded_logs = 0
        self._invalid_logs = {}
        self._num_invalid_logs = 0
        self._INVALID_LOG_THRESHOLD = 0.1 # ratio _num_invalid_logs / _num_loaded_logs at which the sim gap is set to float(inf)
        self._INVALID_LOG_PUNISH_FACTOR = 1.5 # each missing log is punished with 1.5 times the average gap of logs with the same action

    def add(self, action_name: str, recording_date: str, log_index: int):
        new_data = SimulationGapData(self._param_set_id, action_name, recording_date, log_index,
                              self._max_pos, self._max_vel, self._max_acc)
        if new_data.load():
            if action_name not in self._sim_gap_data.keys():
                self._sim_gap_data[action_name] = []
            self._sim_gap_data[action_name].append(new_data)
            self._num_loaded_logs += 1
        else:
            self._num_invalid_logs += 1
            if action_name not in self._invalid_logs.keys():
                self._invalid_logs[action_name] = 1
            else:
                self._invalid_logs[action_name] =+ 1

    def remove(self, action_name: str, recording_date: str, log_index: int):
        """do not  use"""
        if action_name not in self._sim_gap_data.keys():
            return
        for i, gap_object in enumerate(self._sim_gap_data[action_name]):
            if gap_object.recording_date == recording_date and gap_object.log_index == log_index:
                self._sim_gap_data[action_name].pop(i)
        if len(self._sim_gap_data[action_name]) <= 0:
            del self._sim_gap_data[action_name]

    def get(self, action_name: str, recording_date: str, log_index: int) -> Optional[SimulationGapData]:
        if action_name not in self._sim_gap_data.keys():
            return None
        for gap_object in self._sim_gap_data[action_name]:
            if gap_object.recording_date == recording_date and gap_object.log_index == log_index:
                return gap_object
        return None

    def get_all(self, action_name: str) -> list[SimulationGapData]:
        if action_name not in self._sim_gap_data.keys():
            return []
        return self._sim_gap_data[action_name]

    def get_at(self, action_name : str, index : int) -> Optional[SimulationGapData]:
        if action_name in self._sim_gap_data.keys() and len(self._sim_gap_data[action_name]) > index:
            return self._sim_gap_data[action_name][index]
        return None

    def unload(self):
        for gap_data_list in self._sim_gap_data.values():
            for gap_data in gap_data_list:
                gap_data.unload()

    # -------- averages over all replays of the same action --------

    def get_gap_avg_for_joints(self,
                               action_names: Optional[list[str]],
                               method : Callable[[SimulationGapData], dict[str, float]]) \
            -> dict[str, dict[str, float]]:
        """
        Calls the given method for every gap object of the given actions and then averages
        the results for the same action.

        Example: Given the

        :param action_names:
        :param method:
        :return:
        """
        if action_names is None or len(action_names) <= 0:
            action_names = self._sim_gap_data.keys()
        result = {}
        for action_name in action_names:
            result[action_name] = {}
            partial_results : list[dict[str, float]] = []
            weights : list[float] = []
            for gap_object in self._sim_gap_data[action_name]:
                partial_results.append(method(gap_object))
                weights.append(float(gap_object.num_frames))
            for key in partial_results[0].keys():
                partial_results_for_key = [partial_result[key] for partial_result in partial_results]
                result[action_name][key] = np.average(partial_results_for_key, axis=0,weights=weights)
        return result

    def get_gap_avg_for_frames(self,
                               action_names: Optional[list[str]],
                               method: Callable[[SimulationGapData], list[float]]) \
            -> dict[str, list[float]]:
        if action_names is None or len(action_names) <= 0:
            action_names = self._sim_gap_data.keys()
        result = {}
        for action_name in action_names:
            partial_results : list[list[float]]= []
            for gap_object in self._sim_gap_data[action_name]:
                partial_results.append(method(gap_object))
            result[action_name] = [np.nanmean(np.array(group, dtype=float)) for group in zip_longest(*partial_results, fillvalue=np.nan)]
        return result

    def get_gap_avg(self, action_names: Optional[list[str]], method: Callable[[SimulationGapData], float]) -> dict[str, float]:
        if action_names is None or len(action_names) <= 0:
            action_names = list(self._sim_gap_data.keys())
        result = {}
        for action_name in action_names:
            partial_results: list[float] = []
            weights: list[float] = []
            for gap_object in self._sim_gap_data[action_name]:
                partial_results.append(method(gap_object))
                weights.append(gap_object.num_frames)
            result[action_name]= np.average(partial_results, weights=weights)
        return result

    # -------- actual final gap --------

    def get_final_FINAL_gap_avg(self, method: Callable[[SimulationGapData], float]) -> float:
        gap_per_action = self.get_gap_avg(None, method)
        weights = []
        values = []
        for action_name in gap_per_action.keys():
            values.append(gap_per_action[action_name])
            weights.append(sum([gap_object.num_frames for gap_object in self._sim_gap_data[action_name]]))
        return np.average(values, weights=weights)

    def get_optimization_target(self):
        if self._num_loaded_logs == 0:
            # cant revaluate when no logs are loaded
            logger.warning("Attempted calculating the optimization target for 0 loaded logs. Returned float(inf) instead.")
            return float("inf")
        if float(len(self._invalid_logs)) / float(self._num_loaded_logs) > self._INVALID_LOG_THRESHOLD:
            logger.warning("Attempted calculating the optimization target for more than %s invalid logs. Returned float(inf) instead.")
            return float("inf")
        gap_per_action = self.get_gap_avg(None, lambda gap_object: SimulationGapData.get_total_gap_avg(gap_object))
        weights = []
        values = []
        for action_name in gap_per_action.keys():
            gap = gap_per_action[action_name]
            weight = sum([gap_object.num_frames for gap_object in self._sim_gap_data[action_name]])
            if action_name in self._invalid_logs.keys() and self._invalid_logs[action_name] > 0:
                # punish missing logs
                gap_per_run = gap / len(self._sim_gap_data[action_name])
                weight_per_run = weight / len(self._sim_gap_data[action_name])
                gap += gap_per_run * self._INVALID_LOG_PUNISH_FACTOR * self._invalid_logs[action_name]
                weight += weight_per_run * self._invalid_logs[action_name]
                logger.warning("Action %s has invalid logs. Each invalid log is valued as 1.5 times the average gap of the action. %f",
                               action_name, gap_per_run * self._INVALID_LOG_PUNISH_FACTOR)
            weights.append(weight)
            values.append(gap)
        return np.average(values, weights=weights)

    # -------- method to find scale factor --------

    def set_scale_factors(self, max_pos : float, max_vel : float, max_acc : float):
        for gap_list in self._sim_gap_data.values():
            for gap_object in gap_list:
                gap_object.pos_gap_factor = max_pos
                gap_object.vel_gap_factor = max_vel
                gap_object.acc_gap_factor = max_acc

    # -------- properties --------

    @property
    def actions(self) -> list[str]:
        return list(self._sim_gap_data.keys())

    @property
    def max_pos(self) -> float:
        return self._max_pos

    @property
    def max_vel(self) -> float:
        return self._max_vel

    @property
    def max_acc(self) -> float:
        return self._max_acc

    @property
    def loaded_logs(self) -> int:
        return self._num_loaded_logs

    @property
    def num_invalid_logs(self) -> int:
        return self._num_invalid_logs

    # -------- helper methods --------

    def for_each(self, action_names: Optional[list[str]], method : Callable[[SimulationGapData], T]) -> dict[str, list[T]]:
        if action_names is None or len(action_names) <= 0:
            action_names = self._sim_gap_data.keys()
        results = {}
        for action_name in action_names:
            results[action_name] = []
            for gap_data in self._sim_gap_data[action_name]:
                results[action_name].append(method(gap_data))
        return results