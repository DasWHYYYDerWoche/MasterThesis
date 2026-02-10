from __future__ import annotations
from typing import Optional
from enum import Enum
from .Constants import PATH_FIELD_LOGS, PATH_LOGS_AS_CSVS

class ExperimentType(Enum):
    LOG_EXTRACTION = 0
    CSV_REPLAY = 1

class ExperimentData:
    def __init__(self, experiment_type : ExperimentType, action_name : str = "", parameter_set : int = -1, recording_date : str = "", log_index : int = -1, csv_name : str = ""):
        self._experiment_type = experiment_type
        self._action_name: str = action_name
        self._parameter_set: int = parameter_set
        self._recording_date: str = recording_date
        self._log_index: int = log_index
        self._csv_name: str = csv_name

    @property
    def experiment_type(self) -> ExperimentType:
        return self._experiment_type
    @property
    def action_name(self) -> str:
        return self._action_name

    @property
    def parameter_set(self) -> int:
        return self._parameter_set

    @property
    def recording_date(self) -> str:
        return self._recording_date

    @property
    def log_index(self) -> int:
        return self._log_index

    @property
    def csv_name(self) -> str:
        return self._csv_name

    def __str__(self):
        if self._experiment_type is ExperimentType.LOG_EXTRACTION:
            return "ExtractionData: [" + self._action_name + "," + self._recording_date + "," + str(self.log_index) + "]"
        if self._experiment_type is ExperimentType.CSV_REPLAY:
            return "ReplayData: [" + self._action_name + "," + str(self._parameter_set) + "," + self._recording_date + "," + str(self.log_index) + "," + self._csv_name + "]"
        return "ShittyData"


    @staticmethod
    def get_extraction_data(action_name : str, recording_date : str, log_index : int):
        return ExperimentData(experiment_type=ExperimentType.LOG_EXTRACTION, action_name=action_name, recording_date=recording_date, log_index=log_index)

    @staticmethod
    def get_replay_data(action_name : str, parameter_set : int, recording_date : str, csv_name : str):
        return ExperimentData(experiment_type=ExperimentType.CSV_REPLAY, action_name=action_name, parameter_set=parameter_set, recording_date=recording_date, csv_name=csv_name)