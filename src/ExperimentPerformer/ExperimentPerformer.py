from __future__ import annotations
from enum import Enum
from typing import Optional
from datetime import datetime

from ..Utils import ExperimentData, PATH_LOG_EXTRACTION_SCENE, PATH_CSV_REPLAY_SCENE
from ..Simulator import Simulator

import logging
logger = logging.getLogger("global_logger")

class ExperimentMode(Enum):
    FULL = 0
    PARTIAL = 1
    DEL_EXISTING = 2


class ExperimentPerformer:
    def __init__(self):
        self._simulator : Simulator = Simulator()

    def extract(self, action_names: Optional[list[str]] = None,
                recording_dates: Optional[list[str]] = None, log_indices: Optional[list[int]] = None, mode: ExperimentMode = ExperimentMode.PARTIAL, batch_size: int = 5, ):
        """

        :param action_names:
        :param recording_dates:
        :param log_indices:
        :param mode: FULL: extract all given logs, PARTIAL: extract only logs without csv, DEL_EXISTING: delete existing csv of given logs and reextract all
        :param batch_size:
        :return:
        """
        logger.info("Extracting logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        eds = ExperimentData.get_extraction_data(action_names, recording_dates, log_indices)
        if mode == ExperimentMode.PARTIAL:
            eds = ExperimentData.delete_redundant_eds(eds)
        elif mode == ExperimentMode.DEL_EXISTING:
            ExperimentData.delete_existing_csvs(eds)
        ExperimentData.create_directories(eds)
        try:
            self._simulator.run(PATH_LOG_EXTRACTION_SCENE, eds, batch_size)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)

    def replay(self, action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None, log_indices : Optional[list[int]] = None, mode: ExperimentMode = ExperimentMode.PARTIAL, batch_size : int = 5, num_copies : int = 1):
        """

        :param action_names:
        :param recording_dates:
        :param log_indices:
        :param mode: FULL: extract all given logs, PARTIAL: extract only logs with missing csvs, DEL_EXISTING: delete existing csv of given logs and reextract all
        :param batch_size:
        :param num_copies:
        :return:
        """
        if num_copies < 0:
            return
        logger.info("Replaying logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        param_set_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        eds = ExperimentData.get_replay_data(param_set_id, action_names, recording_dates, log_indices, num_copies)
        if mode == ExperimentMode.PARTIAL:
            eds = ExperimentData.delete_redundant_eds(eds)
        elif mode == ExperimentMode.DEL_EXISTING:
            ExperimentData.delete_existing_csvs(eds)
        ExperimentData.create_directories(eds)
        try:
            for _ in range(num_copies):
                self._simulator.run(PATH_CSV_REPLAY_SCENE, eds, batch_size)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)