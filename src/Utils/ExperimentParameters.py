from __future__ import annotations
from typing import Optional
from enum import Enum
from pathlib import Path
from datetime import datetime
from .Constants import PATH_CSV_LOGGER, PATH_FIELD_LOGS, PATH_LOGS_AS_CSVS

import logging
logger = logging.getLogger("global_logger")

class ExperimentType(Enum):
    LOG_EXTRACTION = 0
    CSV_REPLAY = 1

class ExperimentParameters:
    def __init__(self, experiment_type : ExperimentType, param_set_id : str = "", action_name : str = "", recording_date : str = "", log_index : int = -1, num_copies : int = 1):
        self._experiment_type = experiment_type
        self._action_name: str = action_name
        self._param_set_id: str = param_set_id
        self._recording_date: str = recording_date
        self._log_index: int = log_index
        self._num_copies: int = num_copies
        self._num_missing_copies: int = self._count_missing_files()

    def _count_missing_files(self) -> int:
        if self._experiment_type is ExperimentType.LOG_EXTRACTION:
            return 0 if self.log_extraction_path_full.with_suffix(".csv").exists() else 1
        elif self._experiment_type is ExperimentType.CSV_REPLAY:
            path = self.csv_replay_path_full.parent
            if not path.exists():
                return self._num_copies
            existing_files = 0
            for file in path.iterdir():
                if file.name.startswith(str(self._log_index) + "_") and file.suffix == ".csv":
                    existing_files += 1
            return self._num_copies - existing_files
        return 0

    def delete_existing_csv(self):
        if self._experiment_type is ExperimentType.LOG_EXTRACTION:
            file = self.log_extraction_path_full.with_suffix(".csv")
            if file.exists():
                logger.info("Deleted existing csv %s", file)
                file.unlink()
        elif self._experiment_type is ExperimentType.CSV_REPLAY:
            path = self.csv_replay_path_full.parent
            if not path.exists():
                return
            for file in path.iterdir():
                if file.name.startswith(str(self._log_index) + "_"):
                    logger.info("Deleted existing csv %s", file)
                    file.unlink()

    def create_directory(self):
        folder = None
        if self._experiment_type is ExperimentType.LOG_EXTRACTION:
            folder = self.log_extraction_path_full.parent
        elif self._experiment_type is ExperimentType.CSV_REPLAY:
            folder = self.csv_replay_path_full.parent
        if folder and not folder.exists():
            folder.mkdir(parents=True)

    @property
    def experiment_type(self) -> ExperimentType:
        return self._experiment_type

    @property
    def action_name(self) -> str:
        return self._action_name

    @property
    def param_set_id(self) -> str:
        return self._param_set_id

    @property
    def recording_date(self) -> str:
        return self._recording_date

    @property
    def log_index(self) -> int:
        return self._log_index

    @property
    def num_copies(self) -> int:
        return self._num_copies

    @property
    def num_missing_copies(self) -> int:
        return self._num_missing_copies

    @property
    def log_path(self) -> Path:
        return Path("..") / "Logs" / "ThesisFieldLogs"/ self._action_name /  self._recording_date / (str(self._log_index) + ".log")

    @property
    def log_extraction_path_relative(self) -> Path:
        return Path("logsAsCSVs") / self._action_name / self._recording_date / str(self._log_index)

    @property
    def log_extraction_path_full(self) -> Path:
        return PATH_CSV_LOGGER / self.log_extraction_path_relative

    @property
    def csv_replay_path_relative(self) -> Path:
        return Path("replays") / ("paramSet_" + self._param_set_id) / self._action_name / self._recording_date / (str(self._log_index) + "_replayed_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))

    @property
    def csv_replay_path_full(self) -> Path:
        return PATH_CSV_LOGGER / self.csv_replay_path_relative

    def __str__(self):
        if self._experiment_type is ExperimentType.LOG_EXTRACTION:
            return "ExtractionData: [" + self._action_name + "," + self._recording_date + "," + str(self._log_index) + "]"
        if self._experiment_type is ExperimentType.CSV_REPLAY:
            return "ReplayData: [" + str(self._param_set_id) + "," + self._action_name + "," + self._recording_date + "," + str(self._log_index) + "]"
        return "ShittyData"

    # -------- creating extraction data lists from existing files --------

    @staticmethod
    def get_extraction_data(action_names: Optional[list[str]], recording_dates: Optional[list[str]], log_indices : Optional[list[int]]):
        return ExperimentParameters._get_all(ExperimentType.LOG_EXTRACTION, "", action_names, recording_dates, log_indices, 1)

    @staticmethod
    def get_replay_data(param_set_id : str, action_names: Optional[list[str]], recording_dates: Optional[list[str]], log_indices : Optional[list[int]], num_copies : int):
        return ExperimentParameters._get_all(ExperimentType.CSV_REPLAY, param_set_id, action_names, recording_dates, log_indices, num_copies)

    @staticmethod
    def _get_all(experiment_type : ExperimentType, param_set_id : str, action_names: Optional[list[str]], recording_dates: Optional[list[str]], log_indices : Optional[list[int]], num_copies : int) -> \
    list[ExperimentParameters]:
        eds = []
        if action_names is None:
            if experiment_type is ExperimentType.LOG_EXTRACTION:
                action_names = [file.name for file in PATH_FIELD_LOGS.iterdir()]
            elif experiment_type is ExperimentType.CSV_REPLAY:
                action_names = [file.name for file in PATH_LOGS_AS_CSVS.iterdir()]
        for action_name in action_names:
            eds.extend(ExperimentParameters._get_for_action(experiment_type, param_set_id, action_name, recording_dates, log_indices, num_copies))
        return eds

    @staticmethod
    def _get_for_action(experiment_type : ExperimentType, param_set_id : str, action_name: str, recording_dates: Optional[list[str]], log_indices : Optional[list[int]], num_copies : int) -> \
    list[ExperimentParameters]:
        eds = []
        if recording_dates is None:
            if experiment_type is ExperimentType.LOG_EXTRACTION:
                recording_dates = [file.name for file in (PATH_FIELD_LOGS / action_name).iterdir()]
            elif experiment_type is ExperimentType.CSV_REPLAY:
                recording_dates = [file.name for file in (PATH_LOGS_AS_CSVS / action_name).iterdir()]
        for recording_date in recording_dates:
            eds.extend(ExperimentParameters._get_for_action_date(experiment_type, param_set_id, action_name, recording_date, log_indices, num_copies))
        return eds

    @staticmethod
    def _get_for_action_date(experiment_type : ExperimentType, param_set_id : str, action_name : str, recording_date : str, log_indices : Optional[list[int]], num_copies : int) -> list[ExperimentParameters]:
        eds = []
        if log_indices is None:
            if experiment_type is ExperimentType.LOG_EXTRACTION:
                log_indices = [int(file.stem) for file in (PATH_FIELD_LOGS / action_name / recording_date).iterdir()]
            elif experiment_type is ExperimentType.CSV_REPLAY:
                log_indices = [file.name for file in (PATH_LOGS_AS_CSVS / action_name / recording_date).iterdir()]
        if experiment_type is ExperimentType.LOG_EXTRACTION:
            for log_index in log_indices:
                eds.append(ExperimentParameters(experiment_type=ExperimentType.LOG_EXTRACTION, action_name=action_name, recording_date=recording_date, log_index=log_index))
        elif experiment_type is ExperimentType.CSV_REPLAY:
            for log_index in log_indices:
                eds.append(ExperimentParameters(experiment_type=ExperimentType.CSV_REPLAY, param_set_id=param_set_id, action_name=action_name, recording_date=recording_date, log_index=log_index, num_copies=num_copies))
        return eds

    # -------- modifying extraction data lists --------

    @staticmethod
    def delete_existing_csvs(eds : list[ExperimentParameters]):
        for ed in eds:
            ed.delete_existing_csv()

    @staticmethod
    def delete_redundant_eds(eds : list[ExperimentParameters]) -> list[ExperimentParameters]:
        filtered_eds = []
        for ed in eds:
            if ed.num_missing_copies > 0:
                filtered_eds.append(ed)
        return filtered_eds

    @staticmethod
    def create_directories(eds : list[ExperimentParameters]):
        for ed in eds:
            ed.create_directory()