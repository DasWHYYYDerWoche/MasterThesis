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
                gap_object.load()
                partial_results.append(method(gap_object))
                weights.append(float(gap_object.num_frames))
                gap_object.unload()
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
                gap_object.load()
                partial_results.append(method(gap_object))
                gap_object.unload()
            result[action_name] = [np.nanmean(np.array(group, dtype=float)) for group in zip_longest(*partial_results, fillvalue=np.nan)]
        return result

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
                gap_data.load()
                results[action_name].append(method(gap_data))
                gap_data.unload()
        return results