from __future__ import annotations

import pandas
from pathlib import Path
from typing import Optional

from ..Utils import HINGE_NAMES, get_replay_path_full, get_extraction_path_full

import logging
logger = logging.getLogger("global_logger")

class SimulationData:
    def __init__(self, param_set_id: str, action_name: str, recording_date: str, log_index: int):
        self._merged : Optional[pandas.DataFrame] = None
        self._load(param_set_id, action_name, recording_date, log_index)

    def _load(self, param_set_id: str, action_name: str, recording_date: str, log_index: int) -> bool:
        path_replays: Path = get_replay_path_full(param_set_id, action_name, recording_date, log_index).parent
        #load extraction csv
        extraction : Optional[pandas.DataFrame] = pandas.read_csv(get_extraction_path_full(action_name, recording_date, log_index).with_suffix(".csv"),
                                           sep=None, engine="python")
        if extraction is None:
            logger.warning("No extraction at s% exist for log %s", path_replays, log_index)
            return False
        #load replay csv
        replay: Optional[pandas.DataFrame] = None
        for file in path_replays.iterdir():
            if file.name.startswith(str(log_index)):
                replay = pandas.read_csv(path_replays / file.name, sep=None, engine="python")
                break
        if replay is None:
            logger.warning("No replay at s% exist for log %s", path_replays, log_index)
            return False
        #merge extraction and replay
        replay.drop(columns=['time'])
        self._merged = pandas.merge(left=extraction, right=replay, left_on="time", right_on="replayed_frame",
                                                how='inner')
        self._merged.drop(columns=['replayed_frame'])
        logger.info("Successfully loaded replays of log %s",
                    param_set_id + "," + action_name + "," + recording_date + "," + str(log_index))
        return True

    def unload(self):
        self._merged : Optional[pandas.DataFrame] = None