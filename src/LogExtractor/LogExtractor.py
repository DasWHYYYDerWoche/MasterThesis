from __future__ import annotations

from typing import Optional

from ..Simulator import Simulator
from..Utils import PATH_FIELD_LOGS, PATH_CSV_LOGGER, PATH_LOGS_AS_CSVS, ExperimentData, PATH_LOG_EXTRACTION_SCENE

import logging
logger = logging.getLogger("global_logger")

class LogExtractor:
    def __init__(self):
        self._simulator : Simulator = Simulator()

    def extract(self, mode : int = 1, batch_size : int = 5, action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None, log_indices : Optional[list[int]] = None):
        """

        :param mode: 0: extract all logs, 1: extract only not existing logs, 2: extract all and delete existing ones
        :param batch_size:
        :param action_names:
        :param recording_dates:
        :param log_indices:
        :return:
        """
        logger.info("Extracting logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        try:
            eds = ExperimentData.get_extraction_data(action_names, recording_dates, log_indices)
            if mode == 1:
                eds = ExperimentData.delete_redundant_eds(eds)
            elif mode == 2:
                ExperimentData.delete_existing_csvs(eds)
            self._simulator.run(PATH_LOG_EXTRACTION_SCENE, eds, batch_size)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)