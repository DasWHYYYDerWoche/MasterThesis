from __future__ import annotations
from pathlib import Path
from typing import Optional

from ..Utils import PATH_LOGS_AS_CSVS, ExperimentData, PATH_CSV_REPLAY_SCENE
from ..Simulator import Simulator

import logging
logger = logging.getLogger("global_logger")

class CSVReplayer:
    def __init__(self):
        self._simulator : Simulator = Simulator()

    def replay(self, repetitions : int = 1, batch_size : int = 5, action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None, log_indices : Optional[list[int]] = None):
        """

        :param repetitions: how often each csv is replayed
        :param batch_size:
        :param action_names:
        :param recording_dates:
        :param log_indices:
        :return:
        """
        if repetitions < 0:
            return
        logger.info("Extracting logs to csvs, action_names: %s, recording_dates: %s, log_indices: %s",
                    "all" if action_names is None else action_names,
                    "all" if recording_dates is None else recording_dates,
                    "all" if log_indices is None else log_indices)
        try:
            eds = CSVReplayer._get_all(0, action_names, recording_dates, log_indices)
            for _ in range(repetitions):
                self._simulator.run(PATH_CSV_REPLAY_SCENE, eds, batch_size)
        except Exception as e:
            logger.exception("%s failed to run due to %s", type(self).__name__, type(e).__name__)

    @staticmethod
    def _get_all(parameter_set : int, action_names: Optional[list[str]], recording_dates: Optional[list[str]], log_indices : Optional[list[int]]) -> \
    list[ExperimentData]:
        eds = []
        if action_names is None:
            action_names = [file.name for file in PATH_LOGS_AS_CSVS.iterdir()]
        for action_name in action_names:
            eds.extend(CSVReplayer._get_for_action(parameter_set, action_name, recording_dates, log_indices))
        return eds

    @staticmethod
    def _get_for_action(parameter_set : int, action_name: str, recording_dates: Optional[list[str]], log_indices : Optional[list[int]]) -> \
    list[ExperimentData]:
        eds = []
        if recording_dates is None:
            recording_dates = [file.name for file in (PATH_LOGS_AS_CSVS / action_name).iterdir()]
        for recording_date in recording_dates:
            eds.extend(CSVReplayer._get_for_action_date(parameter_set, action_name, recording_date, log_indices))
        return eds

    @staticmethod
    def _get_for_action_date(parameter_set : int, action_name: str, recording_date: str, log_indices : Optional[list[int]]) -> list[
        ExperimentData]:
        eds = []
        csv_names = []
        if log_indices is None:
            csv_names = [file.stem for file in (PATH_LOGS_AS_CSVS / action_name / recording_date).iterdir()]
        else:
            for file_name in [file.stem for file in (PATH_LOGS_AS_CSVS / action_name / recording_date).iterdir()]:
                if int(file_name[0]) in log_indices:
                    csv_names.append(file_name)
        for csv_name in csv_names:
            eds.append(ExperimentData.get_replay_data(action_name, parameter_set, recording_date, csv_name))
        return eds