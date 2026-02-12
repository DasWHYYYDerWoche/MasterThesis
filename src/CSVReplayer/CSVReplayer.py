from __future__ import annotations
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..Utils import PATH_LOGS_AS_CSVS, ExperimentData, PATH_CSV_REPLAY_SCENE
from ..Simulator import Simulator

import logging
logger = logging.getLogger("global_logger")

class CSVReplayer:
    def __init__(self):
        self._simulator : Simulator = Simulator()

    def replay(self, num_copies : int = 1, batch_size : int = 5, action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None, log_indices : Optional[list[int]] = None):
        """

        :param num_copies: how often each csv is replayed
        :param batch_size:
        :param action_names:
        :param recording_dates:
        :param log_indices:
        :return:
        """
        if num_copies < 0:
            return
        logger.info("Extracting logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        try:
            param_set_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            eds = ExperimentData.get_replay_data(param_set_id, action_names, recording_dates, log_indices, num_copies)
            return eds
            for _ in range(repetitions):
                self._simulator.run(PATH_CSV_REPLAY_SCENE, eds, batch_size)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)