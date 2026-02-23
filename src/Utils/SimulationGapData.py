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

class SimulationGapData:
    """
    Simulation gap between a single replay file and the corresponding log
    """
    def __init__(self, param_set_id : str, action_name : str, recording_date : str, log_index : int):

        path_replays: Path = get_replay_path_full(param_set_id, action_name, recording_date, log_index, "").parent
        replays : list[pandas.DataFrame] = []
        for file in path_replays.iterdir():
            if file.name.startswith(str(log_index)):
                replays.append(pandas.read_csv(path_replays / file.name, sep=None, engine="python"))
        if not replays:
            logger.error("No replays at s% exist for log %s", path_replays, log_index)
            return
        self._absolute = {hinge: [0] * len(replays) for hinge in HINGE_NAMES}# target - real
        self._relative_to_target = {hinge: [0] * len(replays) for hinge in HINGE_NAMES}# (target - real) / real
        self._relative_to_range = {hinge: [0] * len(replays) for hinge in HINGE_NAMES}# (target - real) / range
        log : pandas.DataFrame = pandas.read_csv(get_extraction_path_full(action_name, recording_date, log_index).with_suffix(".csv"), sep=None, engine="python")
        log = log.drop(columns=[col for col in log.columns if col.startswith('JR')])
        for i, replay in enumerate(replays):
            replay = replay.drop(columns=['time'])
            joined : pandas.DataFrame = pandas.merge(left=log, right=replay, left_on="time", right_on="replayed_frame", how='inner')
            joined = joined.drop(columns=['replayed_frame'])


            joined.to_csv(path_replays / ("_" + str(i) + ".csv"))
            for hinge_name in HINGE_NAMES:
                joined["JSD_" + hinge_name + "__diff"] = (joined["JSD_" + hinge_name + "_y"] - joined["JSD_" + hinge_name + "_x"])
                joined = joined.sort_index(axis=1)
                self._absolute[hinge_name][i] = joined["JSD_" + hinge_name + "__diff"].mean()
                self._relative_to_target[hinge_name][i] = (joined["JSD_" + hinge_name + "__diff"] / joined["JSD_" + hinge_name + "_x"]).mean()
                self._relative_to_range[hinge_name][i] = (joined["JSD_" + hinge_name + "__diff"] / JOINT_RANGES[hinge_name]).mean()

            joined.to_csv(path_replays / ("_" + str(i) + ".csv"))


    def absolute(self, hinge_name : str) -> list[float]:
        return self._absolute[hinge_name]

    def absolute_avg(self, hinge_name : str) -> float:
        return fmean(self._absolute[hinge_name])

    def relative_to_target(self, hinge_name : str) -> list[float]:
        return self._relative_to_target[hinge_name]

    def relative_to_target_avg(self, hinge_name : str) -> float:
        return fmean(self._relative_to_target[hinge_name])

    def relative_to_range(self, hinge_name : str) -> list[float]:
        return self._relative_to_range[hinge_name]

    def relative_to_range_avg(self, hinge_name : str) -> float:
        return fmean(self._relative_to_range[hinge_name])