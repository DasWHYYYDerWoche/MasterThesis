from __future__ import annotations
from pathlib import Path
from typing import Optional

from ..Utils import ExperimentData, SimulatorData, PATH_LOGS_AS_CSVS, ExperimentData
from ..Simulator import Simulator

import logging
logger = logging.getLogger("global_logger")

class CSVReplayer:
    def __init__(self):
        pass

    def replay(self, mode : int = 1, batch_size : int = 5, action_names : Optional[list[str]] = None, recording_dates : Optional[list[str]] = None, log_indices : Optional[list[int]] = None):
        pass

    @staticmethod
    def _delete_existing_csv(experiment_datas: list[ExperimentData]):
        for ed in experiment_datas:
            folder = PATH_LOGS_AS_CSVS / ed.action_name / ed.recording_date
            if folder.exists():
                for file in folder.iterdir():
                    if file.name.startswith(str(ed.log_index)) and file.suffix == ".csv":
                        logger.info("Deleted existing csv %s", file.name)
                        file.unlink()

    @staticmethod
    def _filter_experiment_datas(experiment_datas: list[ExperimentData]) -> list[ExperimentData]:
        filtered_eds = []
        for ed in experiment_datas:
            folder = PATH_LOGS_AS_CSVS / ed.action_name / ed.recording_date
            if folder.exists():
                found = False
                for file in folder.iterdir():
                    if file.name.startswith(str(ed.log_index)) and file.suffix == ".csv":
                        logger.info("Found existing csv %s and removed corresponding ExtractionData", file.name)
                        found = True
                        break
                if not found:
                    filtered_eds.append(ed)
        return filtered_eds

    @staticmethod
    def _get_all(action_names: Optional[list[str]], recording_dates: Optional[list[str]],
                 log_indices: Optional[list[int]]):
        eds = []
        if action_names is None:
            action_names = [file.name for file in PATH_LOGS_AS_CSVS.iterdir()]
        for action_name in action_names:
            eds.extend(CSVReplayer.get_for_action(action_name, recording_dates, log_indices))
        return eds

    @staticmethod
    def get_for_action(parameter_set : int, action_name: str, recording_dates: Optional[list[str]], log_indices: Optional[list[int]]) -> \
    list[ExperimentData]:
        eds = []
        if recording_dates is None:
            recording_dates = [file.name for file in (PATH_LOGS_AS_CSVS / action_name).iterdir()]
        for recording_date in recording_dates:
            eds.extend(CSVReplayer._get_for_action_date(parameter_set, action_name, recording_date, log_indices))
        return eds

    @staticmethod
    def _get_for_action_date(parameter_set : int, action_name: str, recording_date: str, csv_names: Optional[list[str]]) -> list[
        ExperimentData]:
        eds = []
        if csv_names is None:
            csv_names = [int(file.stem) for file in (PATH_LOGS_AS_CSVS / action_name / recording_date).iterdir()]
        for csv_name in csv_names:
            eds.append(ExperimentData.get_replay_data(action_name, parameter_set, recording_date, csv_name))
        return eds