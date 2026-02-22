from __future__ import annotations

import subprocess
import time
from typing import Optional
from enum import Enum
import math
from pathlib import Path
import pandas
from datetime import datetime

from numpy.ma.extras import average

from .Constants import JOINT_DEFLECTIONS, HINGE_NAMES, get_extraction_path_full, get_replay_path_full
from ..Utils import PATH_EXECUTABLE, ExperimentParameters, ExperimentType, PATH_LOG_EXTRACTION_SCENE, PATH_CSV_REPLAY_SCENE

import logging
logger = logging.getLogger("global_logger")

class SimulationGapData:
    """
    Simulation gap between a single replay file and the corresponding log
    """
    def __init__(self, param_set_id : str, action_name : str, recording_date : str, log_index : int):
        path_replays: Path = get_replay_path_full(param_set_id, action_name, recording_date, log_index, "0").parent
        print(path_replays)
        replays : list[pandas.DataFrame] = []
        for file in path_replays.iterdir():
            if file.name.startswith(str(log_index)):
                replays.append(pandas.read_csv(path_replays / file.name, sep=None, engine="python"))

        if not replays:
            logger.error("No replays at s% exist for log %s", path_replays, log_index)
            return
        self._absolute: dict[str, list[float]] = dict.fromkeys(HINGE_NAMES, [0] * len(replays))  # target - real
        self._relative_to_target: dict[str, list[float]] = dict.fromkeys(HINGE_NAMES, [0] * len(replays))  # (target - real) / real
        self._relative_to_range: dict[str, list[float]] = dict.fromkeys(HINGE_NAMES, [0] * len(replays))  # (target - real) / range
        log : pandas.DataFrame = pandas.read_csv(get_extraction_path_full(action_name, recording_date, log_index).with_suffix(".csv"), sep=None, engine="python")
        log = log.drop(columns=[col for col in log.columns if col.startswith('JR')])
        for i, replay in enumerate(replays):
            print(replay.columns.to_list())
            replay = replay.drop(columns=['time'])
            joined : pandas.DataFrame = pandas.merge(left=log, right=replay, left_on="time", right_on="replayed_frame", how='inner')
            joined = joined.drop(columns=['replayed_frame'])
            joined.to_csv(path_replays / ("_" + str(i) + ".csv"))
            for hinge_name in HINGE_NAMES:
                joined[hinge_name] = joined["JSD_" + hinge_name + "_y"] - joined["JSD_" + hinge_name + "_x"]

            joined.to_csv(path_replays / ("_" + str(i) + ".csv"))


