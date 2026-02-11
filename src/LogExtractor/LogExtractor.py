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
            eds = LogExtractor._get_all(action_names, recording_dates, log_indices)
            if mode == 1:
                eds = LogExtractor._filter_experiment_datas(eds)
            elif mode == 2:
                LogExtractor._delete_existing_csv(eds)
            self._simulator.run(PATH_LOG_EXTRACTION_SCENE, eds, batch_size)
            return eds
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)

    @staticmethod
    def _delete_existing_csv(experiment_datas : list[ExperimentData]):
        for ed in experiment_datas:
            file = (PATH_CSV_LOGGER / ed.log_extraction_path).with_suffix(".csv")
            if file.exists():
                logger.info("Deleted existing csv %s", file)
                file.unlink()

    @staticmethod
    def _filter_experiment_datas(experiment_datas : list [ExperimentData]) -> list[ExperimentData]:
        filtered_eds = []
        for ed in experiment_datas:
            file = (PATH_CSV_LOGGER / ed.log_extraction_path).with_suffix(".csv")
            if file.exists():
                logger.info("Found existing csv %s and removed corresponding ExtractionData", file)
            else:
                filtered_eds.append(ed)
        return filtered_eds

    @staticmethod
    def _get_all(action_names : Optional[list[str]], recording_dates : Optional[list[str]], log_indices : Optional[list[int]]) -> \
    list[ExperimentData]:
        eds = []
        if action_names is None:
            action_names = [file.name for file in PATH_FIELD_LOGS.iterdir()]
        for action_name in action_names:
                eds.extend(LogExtractor._get_for_action(action_name, recording_dates, log_indices))
        return eds

    @staticmethod
    def _get_for_action(action_name : str, recording_dates : Optional[list[str]], log_indices : Optional[list[int]]) -> list[ExperimentData]:
        eds = []
        if recording_dates is None:
            recording_dates = [file.name for file in (PATH_FIELD_LOGS / action_name).iterdir()]
        for recording_date in recording_dates:
            eds.extend(LogExtractor._get_for_action_date(action_name, recording_date, log_indices))
        return eds

    @staticmethod
    def _get_for_action_date(action_name : str, recording_date : str, log_indices : Optional[list[int]]) -> list[ExperimentData]:
        eds = []
        if log_indices is None:
            log_indices = [int(file.stem) for file in (PATH_FIELD_LOGS / action_name / recording_date).iterdir()]
        for log_index in log_indices:
            eds.append(ExperimentData.get_extraction_data(action_name, recording_date, log_index))
        return eds