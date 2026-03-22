from __future__ import annotations

from itertools import zip_longest
from statistics import fmean

import numpy as np
import pandas
from pathlib import Path
from typing import Optional, Callable, TypeVar

from pandas.core.window.doc import numba_notes

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

    def get_at(self, action_name : str, index : int) -> Optional[SimulationGapData]:
        if action_name in self._sim_gap_data.keys() and len(self._sim_gap_data[action_name]) > index:
            return self._sim_gap_data[action_name][index]
        return None

    # -------- getters that combine results of all gap_objects for a single action --------

    def get_all(self, action_name : str,
                method : Callable[[SimulationGapData, Optional[list[str]], int, int], dict[str, list[float]]],
                hinge_names: Optional[list[str]] = None,
                start_frame: int = 0,
                end_frame: int = -1) \
            -> dict[str, list[tuple[float]]]:
        """
        Calls the given method for all gap_objects with the given action.
        The returned dictionary has the following structure:

        The inner tuple contains an entry for each existing gap_object with the given action.

        The lists contain a tuple for every requested frame.

        The dictionary has an entry for every requested joint.

        :param method: get_pos_extraction, get_vel_extraction, get_acc_extraction,
            get_pos_replay, get_vel_replay, get_acc_replay, get_pos_gap, get_vel_gap, get_acc_gap, get_total_gap
        """
        result_as_list = self._get_for_all(action_name, method, hinge_names,start_frame,end_frame)
        if len(result_as_list) <= 0:
            return {}
        result = {key : [] for key in result_as_list[0].keys()}
        for key in result.keys():
            results_for_key : list[list[float]] = []
            for partial_result in result_as_list:
                results_for_key.append(partial_result[key])
            result[key] = list(zip_longest(*results_for_key, fillvalue=float('nan')))
        return result

    def get_all_gap_avg_for_joints(self, action_name : str,
                                   method : Callable[[SimulationGapData, Optional[list[str]], int, int], dict[str, float]],
                                   hinge_names: Optional[list[str]] = None,
                                   start_frame: int = 0,
                                   end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Calls the given method for all gap_objects with the given action.
        The returned dictionary has the following structure:

        The inner list contains an entry for each existing gap_object with the given action.

        The dictionary has an entry for every requested joint.

        :param method: get_pos_gap_avg_for_joints, get_vel_gap_avg_for_joints get_acc_gap_avg_for_joints, get_total_gap_avg_for_joints
        """
        result_as_list = self._get_for_all(action_name, method, hinge_names,start_frame,end_frame)
        if len(result_as_list) <= 0:
            return {}
        result = {key : [] for key in result_as_list[0].keys()}
        for key in result.keys():
            result[key] = [partial_result[key] for partial_result in result_as_list]
        return result

    def get_all_gap_avg_for_frames(self, action_name : str,
                                   method : Callable[[SimulationGapData, Optional[list[str]], int, int], list[float]],
                                   hinge_names: Optional[list[str]] = None,
                                   start_frame: int = 0,
                                   end_frame: int = -1)\
            -> list[tuple[float]]:
        """
        Calls the given method for all gap_objects with the given action.
        The returned list has the following structure:

        The inner tuple contains an entry for each existing gap_object with the given action.

        The list has an entry for every requested frame.
        :param method: get_pos_gap_avg_for_frames, get_vel_gap_avg_for_frames, get_acc_gap_avg_for_frames, get_total_gap_avg_for_frames
        """
        result_as_list = self._get_for_all(action_name, method, hinge_names,start_frame,end_frame)
        if len(result_as_list) <= 0:
            return []
        return list(zip_longest(*result_as_list, fillvalue=float('nan')))

    # -------- averages over all replays of the same action --------

    def get_gap_avg_for_joints(self,
                               action_names: Optional[list[str]],
                               method: Callable[[SimulationGapData, Optional[list[str]], int, int], dict[str, float]],
                               hinge_names: Optional[list[str]] = None,
                               start_frame: int = 0,
                               end_frame: int = -1) \
            -> dict[str, dict[str, float]]:
        if action_names is None or len(action_names) <= 0:
            action_names = self._sim_gap_data.keys()
        result = {}
        for action_name in action_names:
            result[action_name] = {joint_name : fmean(gap_list) for joint_name,gap_list in
                self.get_all_gap_avg_for_joints(action_name, method, hinge_names, start_frame,end_frame).items()}
        return result

    def get_gap_avg_for_frames(self,
                               action_names: Optional[list[str]],
                               method: Callable[[SimulationGapData, Optional[list[str]], int, int], list[float]],
                               hinge_names: Optional[list[str]] = None,
                               start_frame: int = 0,
                               end_frame: int = -1) \
            -> dict[str, list[float]]:
        if action_names is None or len(action_names) <= 0:
            action_names = self._sim_gap_data.keys()
        result = {}
        for action_name in action_names:
            result[action_name] = [fmean(gap_list) for gap_list in
                self.get_all_gap_avg_for_frames(action_name, method, hinge_names, start_frame,end_frame)]
        return result

    # ???

    def get_gap_data_for_frames(self,
                                action_name: str,
                                method: Callable[[SimulationGapData, Optional[list[str]], int, int], list[float]],
                                hinge_names: Optional[list[str]] = None,
                                start_frame: int = 0,
                                end_frame: int = -1,
                                factor : int = 1) \
            -> list[tuple[float, float, float]]:
        partial_results = self.get_all_gap_avg_for_frames(action_name, method, hinge_names, start_frame, end_frame)
        val = [(t,t,t) for t in partial_results]







    # -------- properties --------

    @property
    def actions(self) -> list[str]:
        return list(self._sim_gap_data.keys())

    # -------- helper methods --------

    def _get_for_all(self, action_name : str,
                           method : Callable[[SimulationGapData, Optional[list[str]], int, int], T],
                           hinge_names: Optional[list[str]] = None,
                           start_frame: int = 0,
                           end_frame: int = -1) -> list[T]:
        if not action_name in self._sim_gap_data.keys():
            return []
        results = []
        for gap_object in self._sim_gap_data[action_name]:
            gap_object.load()
            results.append(method(gap_object, hinge_names, start_frame, end_frame))
            gap_object.unload()
        return results