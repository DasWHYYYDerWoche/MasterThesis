from __future__ import annotations

import subprocess
import time
from typing import Optional
from enum import Enum
import math
from pathlib import Path
import pandas
from statistics import fmean
from datetime import datetime

from numpy.ma.extras import average

from .Constants import JOINT_RANGES, HINGE_NAMES, get_extraction_path_full, get_replay_path_full
from ..Utils import PATH_EXECUTABLE, ExperimentParameters, ExperimentType, PATH_LOG_EXTRACTION_SCENE, PATH_CSV_REPLAY_SCENE

import logging
logger = logging.getLogger("global_logger")

class DataSelector(Enum):
    EXTRACTION = 0
    REPLAY = 1
    MERGED = 2

class SimulationGapData:

    def __init__(self, param_set_id: str, action_name: str, recording_date: str, log_index: int):
        self._merged : Optional[pandas.DataFrame] = None
        self._param_set_id: str = param_set_id
        self._action_name: str = action_name
        self._recording_date: str = recording_date
        self._log_index: int = log_index

    def load(self) -> bool:
        path_replays: Path = get_replay_path_full(self._param_set_id, self._action_name, self._recording_date, self._log_index).parent
        #load extraction csv
        extraction : Optional[pandas.DataFrame] = pandas.read_csv(get_extraction_path_full(self._action_name, self._recording_date, self._log_index).with_suffix(".csv"),
                                           sep=None, engine="python")
        if extraction is None:
            logger.warning("No extraction at s% exist for log %s", path_replays, self._log_index)
            return False
        #load replay csv
        replay: Optional[pandas.DataFrame] = None
        for file in path_replays.iterdir():
            if file.name.startswith(str(self._log_index)):
                replay = pandas.read_csv(path_replays / file.name, sep=None, engine="python")
                break
        if replay is None:
            logger.warning("No replay at s% exist for log %s", path_replays, self._log_index)
            return False
        #merge extraction and replay
        replay.drop(columns=['time'])
        self._merged = pandas.merge(left=extraction, right=replay, left_on="time", right_on="replayed_frame",
                                                how='inner')
        self._merged.drop(columns=['replayed_frame'])
        logger.info("Successfully loaded replays of log %s",
                    self._param_set_id + "," + self._action_name + "," + self._recording_date + "," + str(self._log_index))
        return True

    def unload(self):
        self._merged : Optional[pandas.DataFrame] = None

    def get_pos_extraction(self, hinge_names: Optional[list[str]] = None, row_start: int = 0, row_end: int = -1):
        if row_start < 0:
            row_start = 0
        if row_end == -1:
            row_end = len(self._merged.index)
        if row_start >= row_end:
            return {}
        if hinge_names is None:
            hinge_names = HINGE_NAMES
        dic = {hinge_name : [] for hinge_name in hinge_names}
        for hinge_name in hinge_names:
            dic[hinge_name] = ((self._merged["JSD_" + hinge_name + "_x"])[row_start:row_end]).to_list()
        return dic

    def get_pos_replay(self, hinge_names: Optional[list[str]] = None, row_start: int = 0, row_end: int = -1):
        if row_start < 0:
            row_start = 0
        if row_end == -1:
            row_end = len(self._merged.index)
        if row_start >= row_end:
            return {}
        if hinge_names is None:
            hinge_names = HINGE_NAMES
        dic = {hinge_name : [] for hinge_name in hinge_names}
        for hinge_name in hinge_names:
            dic[hinge_name] = ((self._merged["JSD_" + hinge_name + "_y"])[row_start:row_end]).to_list()
        return dic

    def get_pos_gap(self, hinge_names: Optional[list[str]] = None, row_start: int = 0, row_end: int = -1) -> dict[str, list[float]]:
        d_extraction = self.get_pos_extraction(hinge_names, row_start, row_end)
        d_replay = self.get_pos_replay(hinge_names, row_start, row_end)
        dic = {}
        for hinge_name in d_extraction.keys():
            dic[hinge_name] = [pow(p_replay - p_extraction, 2) for p_extraction, p_replay in zip(d_extraction[hinge_name], d_replay[hinge_name])]
        return dic

    def get_vel_extraction(self, hinge_names: Optional[list[str]] = None, row_start: int = 1, row_end: int = -1) -> dict[str, list[float]]:
        dic : dict[str, list[float]] = self.get_pos_extraction(hinge_names, row_start-1, row_end)
        for key in dic.keys():
            val = dic[key]
            dic[key] = [p1 - p0 for p0,p1 in zip(val[:-1], val[1:])]
        return dic

    def get_vel_replay(self, hinge_names: Optional[list[str]] = None, row_start: int = 1, row_end: int = -1) -> dict[str, list[float]]:
        dic : dict[str, list[float]] = self.get_pos_replay(hinge_names, row_start-1, row_end)
        for key in dic.keys():
            val = dic[key]
            dic[key] = [p1 - p0 for p0,p1 in zip(val[:-1], val[1:])]
        return dic

    def get_vel_gap(self, hinge_names: Optional[list[str]] = None, row_start: int = 1, row_end: int = -1) -> dict[str, list[float]]:
        d_extraction = self.get_vel_extraction(hinge_names, row_start, row_end)
        d_replay = self.get_vel_replay(hinge_names, row_start, row_end)
        dic = {}
        for hinge_name in d_extraction.keys():
            dic[hinge_name] = [pow(v_replay - v_extraction, 2) for v_extraction, v_replay in
                               zip(d_extraction[hinge_name], d_replay[hinge_name])]
        return dic

    def get_acc_extraction(self, hinge_names: Optional[list[str]] = None, row_start: int = 2, row_end: int = -1) -> dict[str, list[float]]:
        dic : dict[str, list[float]] = self.get_vel_extraction(hinge_names, row_start-1, row_end)
        for key in dic.keys():
            val = dic[key]
            dic[key] = [p1 - p0 for p0,p1 in zip(val[:-1], val[1:])]
        return dic

    def get_acc_replay(self, hinge_names: Optional[list[str]] = None, row_start: int = 2, row_end: int = -1) -> dict[str, list[float]]:
        dic : dict[str, list[float]] = self.get_vel_replay(hinge_names, row_start-1, row_end)
        for key in dic.keys():
            val = dic[key]
            dic[key] = [p1 - p0 for p0,p1 in zip(val[:-1], val[1:])]
        return dic

    def get_acc_gap(self, hinge_names: Optional[list[str]] = None, row_start: int = 2, row_end: int = -1) -> dict[str, list[float]]:
        d_extraction = self.get_acc_extraction(hinge_names, row_start, row_end)
        d_replay = self.get_acc_replay(hinge_names, row_start, row_end)
        dic = {}
        for hinge_name in d_extraction.keys():
            dic[hinge_name] = [pow(a_replay - a_extraction, 2) for a_extraction, a_replay in
                               zip(d_extraction[hinge_name], d_replay[hinge_name])]
        return dic

    def get_total_gap(self, hinge_names: Optional[list[str]] = None, row_start: int = 0, row_end: int = -1) -> dict[str, list[float]]:
        d_p = self.get_pos_gap(hinge_names, row_start, row_end)
        d_v = self.get_vel_gap(hinge_names, row_start, row_end) # 1 shorter if row_start = 0
        d_a = self.get_acc_gap(hinge_names, row_start, row_end) # 1 shorter if row_start = 0 and 2 shorter if row_start = 1
        d_total = {}
        for hinge in d_p.keys():
            l_p = d_p[hinge]
            l_v = d_v[hinge]
            l_a = d_a[hinge]
            if row_start <= 1:
                l_a = [0] + l_a
            if row_start <= 0:
                l_a = [0] + l_a
                l_v = [0] + l_v
            d_total[hinge] = [p + v + a for p,v,a in zip(l_p, l_v, l_a)]
        return d_total




    @property
    def identifier(self) -> str:
        return self._param_set_id + ";" + self._action_name + ";" + self._recording_date + ";" + str(self._log_index)

    @property
    def param_set_id(self) -> str:
        return self._param_set_id

    @property
    def action_name(self) -> str:
        return self._action_name

    @property
    def recording_date(self) -> str:
        return self._recording_date

    @property
    def log_index(self) -> int:
        return self._log_index