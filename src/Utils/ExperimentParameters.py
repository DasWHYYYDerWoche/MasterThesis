from __future__ import annotations
from typing import Optional
from enum import Enum
from copy import copy
from pathlib import Path
from datetime import datetime
from .Constants import (PATH_FIELD_LOGS, PATH_LOGS_AS_CSVS,
                        get_field_logs_path, get_replay_path_full, get_replay_path_partial,get_extraction_path_partial,get_extraction_path_full)

import logging
logger = logging.getLogger("global_logger")

class ExperimentType(Enum):
    LOG_EXTRACTION = 0
    CSV_REPLAY = 1


class ExperimentMode(Enum):
    FULL = 0
    PARTIAL = 1
    DEL_EXISTING = 2

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
            return 0 if self.extraction_path_full.with_suffix(".csv").exists() else 1
        elif self._experiment_type is ExperimentType.CSV_REPLAY:
            path = self.replay_path_full.parent
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
            file = self.extraction_path_full.with_suffix(".csv")
            if file.exists():
                logger.info("Deleted existing csv %s", file)
                file.unlink()
        elif self._experiment_type is ExperimentType.CSV_REPLAY:
            path = self.replay_path_full.parent
            if not path.exists():
                return
            for file in path.iterdir():
                if file.name.startswith(str(self._log_index) + "_"):
                    logger.info("Deleted existing csv %s", file)
                    file.unlink()
        self._num_missing_copies = self._count_missing_files()

    def create_directory(self):
        folder = None
        if self._experiment_type is ExperimentType.LOG_EXTRACTION:
            folder = self.extraction_path_full.parent
        elif self._experiment_type is ExperimentType.CSV_REPLAY:
            folder = self.replay_path_full.parent
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
        return get_field_logs_path(self._action_name, self._recording_date, self._log_index)

    @property
    def extraction_path_relative(self) -> Path:
        return get_extraction_path_partial(self._action_name, self._recording_date, self._log_index)

    @property
    def extraction_path_full(self) -> Path:
        return get_extraction_path_full(self._action_name, self._recording_date, self._log_index)

    @property
    def replay_path_relative(self) -> Path:
        return get_replay_path_partial(self._param_set_id, self._action_name, self._recording_date, self._log_index)

    @property
    def replay_path_full(self) -> Path:
        return get_replay_path_full(self._param_set_id, self._action_name, self._recording_date, self._log_index)

    def __str__(self):
        if self._experiment_type is ExperimentType.LOG_EXTRACTION:
            return "ExtractionData: [" + self._action_name + "," + self._recording_date + "," + str(self._log_index) + "]"
        if self._experiment_type is ExperimentType.CSV_REPLAY:
            return "ReplayData: [" + str(self._param_set_id) + "," + self._action_name + "," + self._recording_date + "," + str(self._log_index) + "]"
        return "ShittyData"

    # -------- creating extraction data lists from existing files --------

    @staticmethod
    def get_extraction_data(action_names: Optional[list[str]] = None,
                            recording_dates: Optional[list[str]] = None,
                            log_indices : Optional[list[int]] = None,
                            mode: ExperimentMode = ExperimentMode.PARTIAL) -> list[ExperimentParameters]:
        if mode is ExperimentMode.FULL:
            logger.warning("Logs cannot be extracted multiple times. Chose an extraction mode other than FULL")
            return []
        eps = ExperimentParameters._get_all(ExperimentType.LOG_EXTRACTION, "", action_names, recording_dates, log_indices, 1)
        ExperimentParameters._prepare(eps, mode)
        return eps

    @staticmethod
    def get_replay_data(param_set_id : str,
                        action_names: Optional[list[str]] = None,
                        recording_dates: Optional[list[str]] = None,
                        log_indices : Optional[list[int]] = None,
                        num_copies : int = 1,
                        mode: ExperimentMode = ExperimentMode.PARTIAL) -> list[ExperimentParameters]:
        eps = ExperimentParameters._get_all(ExperimentType.CSV_REPLAY, param_set_id, action_names, recording_dates, log_indices, num_copies)
        ExperimentParameters._prepare(eps, mode)
        return eps

    @staticmethod
    def _get_all(experiment_type : ExperimentType,
                 param_set_id : str,
                 action_names: Optional[list[str]],
                 recording_dates: Optional[list[str]],
                 log_indices : Optional[list[int]],
                 num_copies : int) -> list[ExperimentParameters]:
        eps = []
        if action_names is None:
            if experiment_type is ExperimentType.LOG_EXTRACTION:
                action_names = [file.name for file in PATH_FIELD_LOGS.iterdir()]
            elif experiment_type is ExperimentType.CSV_REPLAY:
                action_names = [file.name for file in PATH_LOGS_AS_CSVS.iterdir()]
        for action_name in action_names:
            eps.extend(ExperimentParameters._get_for_action(experiment_type, param_set_id, action_name, recording_dates, log_indices, num_copies))
        return eps

    @staticmethod
    def _get_for_action(experiment_type : ExperimentType,
                        param_set_id : str,
                        action_name: str,
                        recording_dates: Optional[list[str]],
                        log_indices : Optional[list[int]],
                        num_copies : int) -> list[ExperimentParameters]:
        eps = []
        if recording_dates is None:
            if experiment_type is ExperimentType.LOG_EXTRACTION:
                recording_dates = [file.name for file in (PATH_FIELD_LOGS / action_name).iterdir()]
            elif experiment_type is ExperimentType.CSV_REPLAY:
                recording_dates = [file.name for file in (PATH_LOGS_AS_CSVS / action_name).iterdir()]
        for recording_date in recording_dates:
            eps.extend(ExperimentParameters._get_for_action_date(experiment_type, param_set_id, action_name, recording_date, log_indices, num_copies))
        return eps

    @staticmethod
    def _get_for_action_date(experiment_type : ExperimentType,
                             param_set_id : str, action_name : str,
                             recording_date : str,
                             log_indices : Optional[list[int]],
                             num_copies : int) -> list[ExperimentParameters]:
        eps = []
        if log_indices is None:
            if experiment_type is ExperimentType.LOG_EXTRACTION:
                log_indices = [int(file.stem) for file in (PATH_FIELD_LOGS / action_name / recording_date).iterdir()]
            elif experiment_type is ExperimentType.CSV_REPLAY:
                log_indices = [file.name for file in (PATH_LOGS_AS_CSVS / action_name / recording_date).iterdir()]
        if experiment_type is ExperimentType.LOG_EXTRACTION:
            for log_index in log_indices:
                eps.append(ExperimentParameters(experiment_type=ExperimentType.LOG_EXTRACTION, action_name=action_name, recording_date=recording_date, log_index=log_index))
        elif experiment_type is ExperimentType.CSV_REPLAY:
            for log_index in log_indices:
                eps.append(ExperimentParameters(experiment_type=ExperimentType.CSV_REPLAY, param_set_id=param_set_id, action_name=action_name, recording_date=recording_date, log_index=log_index, num_copies=num_copies))
        return eps

    # -------- modifying extraction data lists --------

    @staticmethod
    def _prepare(eps : list[ExperimentParameters], mode: ExperimentMode):
        if mode == ExperimentMode.PARTIAL:
            for i, ep in enumerate(eps):
                if ep._num_missing_copies < 1:
                    eps.pop(i)
        elif mode == ExperimentMode.DEL_EXISTING:
            for ep in eps:
                ep.delete_existing_csv()
        for ep in eps:
            ep.create_directory()