from __future__ import annotations
from itertools import zip_longest
import numpy as np
from typing import Optional, Callable, TypeVar

from .SimulationGapData import SimulationGapData

import logging
logger = logging.getLogger("global_logger")

T = TypeVar("T")

class SimulationGapHandler:
    def __init__(self, param_set_id: str):
        self._sim_gap_data : dict[str, list[SimulationGapData]] = {}
        self._param_set_id: str = param_set_id

    def add(self, action_name: str, recording_date: str, log_index: int):
        if action_name not in self._sim_gap_data.keys():
            self._sim_gap_data[action_name] = []
        self._sim_gap_data[action_name].append(SimulationGapData(self._param_set_id, action_name, recording_date, log_index))

    def remove(self, action_name: str, recording_date: str, log_index: int):
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

    # -------- averages over all replays of the same action --------

    def get_gap_avg_for_joints(self,
                               action_names: Optional[list[str]],
                               method : Callable[[SimulationGapData], dict[str, float]]) \
            -> dict[str, dict[str, float]]:
        if action_names is None or len(action_names) <= 0:
            action_names = self._sim_gap_data.keys()
        result = {}
        for action_name in action_names:
            result[action_name] = {}
            partial_results : list[dict[str, float]]= []
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
            weights.append(sum([gap_object.num_frames for gap_object in self._sim_gap_data[action_name]]))
            values.append(gap_per_action[action_name])
        return np.average(values, weights=weights)

    # -------- method to find scale factor --------

    def avg_abs_pos(self) -> float:
        averages = []
        weights = []
        for gap_objects in self._sim_gap_data.values():
            cur_weights = [gap_object.num_frames for gap_object in gap_objects]
            averages.append(np.average([gap_object.avg_abs_pos() for gap_object in gap_objects], weights=cur_weights))
            weights.append(len(cur_weights))
        return np.average(averages, weights=weights)

    def avg_abs_vel(self) -> float:
        averages = []
        weights = []
        for gap_objects in self._sim_gap_data.values():
            cur_weights = [gap_object.num_frames for gap_object in gap_objects]
            averages.append(np.average([gap_object.avg_abs_vel() for gap_object in gap_objects], weights=cur_weights))
            weights.append(len(cur_weights))
        return np.average(averages, weights=weights)

    def avg_abs_acc(self) -> float:
        averages = []
        weights = []
        for gap_objects in self._sim_gap_data.values():
            cur_weights = [gap_object.num_frames for gap_object in gap_objects]
            averages.append(np.average([gap_object.avg_abs_acc() for gap_object in gap_objects], weights=cur_weights))
            weights.append(len(cur_weights))
        return np.average(averages, weights=weights)

    def max_abs_pos(self) -> float:
        return max([max([gap_object.max_abs_pos() for gap_object in gap_objects])
                    for gap_objects in self._sim_gap_data.values()])

    def max_abs_vel(self) -> float:
        return max([max([gap_object.max_abs_vel() for gap_object in gap_objects])
                    for gap_objects in self._sim_gap_data.values()])

    def max_abs_acc(self) -> float:
        return max([max([gap_object.max_abs_acc() for gap_object in gap_objects])
                    for gap_objects in self._sim_gap_data.values()])

    def get_scale_factors(self) -> tuple[float,float]:
        avg_pos = self.avg_abs_pos()
        avg_vel = self.avg_abs_vel()
        avg_acc = self.avg_abs_acc()
        print(avg_pos)
        print(avg_vel)
        print(avg_acc)
        return avg_pos / avg_vel, avg_pos / avg_acc

    def set_scale_factors(self, vel_gap_factor: float, acc_gap_factor : float):
        for gap_list in self._sim_gap_data.values():
            for gap_object in gap_list:
                gap_object.vel_gap_factor = vel_gap_factor
                gap_object.acc_gap_factor = acc_gap_factor

    # -------- properties --------

    @property
    def actions(self) -> list[str]:
        return list(self._sim_gap_data.keys())

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