from __future__ import annotations

from itertools import zip_longest

import numpy as np
import pandas
from pathlib import Path
from typing import Optional

from pandas.core.window.doc import numba_notes

from .SimulationGapData import SimulationGapData

import logging
logger = logging.getLogger("global_logger")

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

    def get(self, action_names: Optional[list[str]] = None, recording_dates: Optional[list[str]] = None, log_indices: Optional[list[int]] = None) -> list[SimulationGapData]:
        if action_names is None:
            action_names = list(self._sim_gap_data.keys())
        ret = []
        for action_name in action_names:
            if action_name in self._sim_gap_data.keys():
                ret.extend(self._sim_gap_data[action_name])
        if recording_dates is not None:
            ret = [gab_object for gab_object in ret if gab_object.recording_date in recording_dates]
        if log_indices is not None:
            ret = [gab_object for gab_object in ret if gab_object.recording_date in recording_dates]
        return ret

    def get_at(self, action_name : str, index : int) -> Optional[SimulationGapData]:
        if action_name in self._sim_gap_data.keys() and len(self._sim_gap_data[action_name]) > index:
            return self._sim_gap_data[action_name][index]
        return None

    # -------- averages over all replays of the same action --------

    def get_avg_for_joints(self,
                           action_name : str,
                           hinge_names: Optional[list[str]] = None,
                           start_frame: int = 0,
                           end_frame: int = -1)\
            -> dict[str, float]:
        """
        Returns the average simulation gap of the given joints for the given action as a dictionary.
        """
        if not action_name in self._sim_gap_data.keys():
            return {}
        frame_avgs_list: list[dict[str, float]]= []
        for gap_object in self._sim_gap_data[action_name]:
            gap_object.load()
            frame_avgs_list.append(gap_object.get_pos_gap_avg_for_joints(hinge_names, start_frame, end_frame))
            gap_object.unload()
        num_logs = len(frame_avgs_list)
        if len(frame_avgs_list) == 0:
            return {}
        if len(frame_avgs_list) == 1:
            return frame_avgs_list[0]
        result = {key :value for key,value in frame_avgs_list[0].items()}
        for frame_avgs_dic in frame_avgs_list[1:]:
            for joint_name, frame_avg in frame_avgs_dic.items():
                result[joint_name] += frame_avg
        for key in result.keys():
            result[key] = result[key] / num_logs
        return result

    def get_avg_for_frames(self,
                           action_name : str,
                           hinge_names: Optional[list[str]] = None,
                           start_frame: int = 0,
                           end_frame: int = -1)\
            -> list[float]:
        """
        Returns the average simulation gap of the given frames for the given action as a list.
        """
        if not action_name in self._sim_gap_data.keys():
            return []
        joint_avgs = []
        for gap_object in self._sim_gap_data[action_name]:
            gap_object.load()
            joint_avgs.append(gap_object.get_pos_gap_avg_for_frames(hinge_names, start_frame, end_frame))
            gap_object.unload()
        result = [0 for _ in range(max([len(joint_avg) for joint_avg in joint_avgs]))]
        div_at = [0 for _ in range(max([len(joint_avg) for joint_avg in joint_avgs]))]
        for i, joint_avg in enumerate(joint_avgs):
            for avg_at_frame in joint_avg:
                result[i] += avg_at_frame
                div_at[i] += 1
        return [val / div for val, div in zip(result, div_at)]

    # -------- properties --------

    @property
    def actions(self) -> list[str]:
        return list(self._sim_gap_data.keys())