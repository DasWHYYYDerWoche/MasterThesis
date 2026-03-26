from __future__ import annotations
from enum import Enum
from pathlib import Path
from typing import Optional
from .Constants import (PATH_FIELD_LOGS, PATH_LOGS_AS_CSVS,
                        get_field_logs_path_partial, get_replay_path_full,
                       get_replay_path_partial, get_extraction_path_partial,
                       get_extraction_path_full, get_field_logs_path_full)

import logging
logger = logging.getLogger("global_logger")

class ExperimentType(Enum):
    LOG_EXTRACTION = 0
    CSV_REPLAY = 1

class ExperimentMode(Enum):
    FULL = 0 #TODO full doesnt make any sense if everything is extracted at most once
    PARTIAL = 1
    DEL_EXISTING = 2

class ExperimentParameters:
    """
    Holds all information needed to perform a single experiment. Used to transfer information between different parts of the project.
    Also provides a host of static method to generate lists of experiment parameters based on existing files.
    """

    def __init__(self, param_set_id : Optional[str], action_name : str, recording_date : str, log_index : int):

        """
        :param param_set_id: which parameter set to use
        :param action_name: one of "kick", "turn", "sidestep", "walk"
        :param recording_date: data when the original log was recorded
        :param log_index: number of the log
        """
        self._action_name: str = action_name
        self._param_set_id: str = param_set_id
        self._recording_date: str = recording_date
        self._log_index: int = log_index

    def exists_log(self) -> bool:
        """
        :return: True if a .log file exists, False otherwise
        """
        return self.log_path_full.exists()

    def exists_extraction(self) -> bool:
        """

        :return: True if an extraction .csv of the .log file exists
        """
        return self.extraction_path_full.with_suffix(".csv").exists()

    def exists_replay(self) -> bool:
        """

        :return: True if a replay .csv of the extraction exists
        """
        path = self.replay_path_full.parent
        if not path.exists():
            return False
        for file in path.iterdir():
            if file.name.startswith(str(self._log_index) + "_") and file.suffix == ".csv":
                return True
        return False

    def delete_target(self) -> bool:
        """
        Deletes the target file if it exists
        :return: True if the file existed and was deleted, False otherwise
        """
        if self._param_set_id is None:
            file = self.extraction_path_full.with_suffix(".csv")
            if file.exists():
                logger.info("Deleted extraction %s", file)
                file.unlink()
                return True
            return False
        else:
            path = self.replay_path_full.parent
            if not path.exists():
                return False
            for file in path.iterdir():
                if file.name.startswith(str(self._log_index) + "_"):
                    logger.info("Deleted replay %s", file)
                    file.unlink()
                    return True
            return False

    def create_directories(self):
        """
        Creates the directories of the extraction and replay if they do not exist.
        """
        folder = self.extraction_path_full.parent
        if not folder.exists():
            folder.mkdir(parents=True)
        if self._param_set_id is not None:
            folder = self.replay_path_full.parent
            if not folder.exists():
                folder.mkdir(parents=True)

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
    def log_path_relative(self) -> Path:
        return get_field_logs_path_partial(self._action_name, self._recording_date, self._log_index)

    @property
    def log_path_full(self) -> Path:
        return get_field_logs_path_full(self._action_name, self._recording_date, self._log_index)

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
        if self._param_set_id is None:
            return "ExtractionData: [" + self._action_name + "," + self._recording_date + "," + str(self._log_index) + "]"
        else:
            return "ReplayData: [" + str(self._param_set_id) + "," + self._action_name + "," + self._recording_date + "," + str(self._log_index) + "]"

    # -------- creating extraction data lists from existing files --------

    @staticmethod
    def create_experiment_parameters(param_set_id : Optional[str],
                                     data : Optional[list[tuple[Optional[str], Optional[str], Optional[int]]]])\
            -> list[ExperimentParameters]:
        if data is None:
            return ExperimentParameters._create_experiment_parameters(param_set_id, None, None, None)
        else:
            eps = []
            for a_n, r_d, l_i in data:
                eps.extend(ExperimentParameters._create_experiment_parameters(param_set_id, a_n, r_d, l_i))
            return eps

    @staticmethod
    def _create_experiment_parameters(param_set_id : Optional[str],
                                      action_name : Optional[str],
                                      recording_date : Optional[str],
                                      log_index : Optional[int]) \
            -> list[ExperimentParameters]:
        """
        Creates an ExperimentParameter object for the given parameters. If any of action_name, recording_date or log_index are None they are replaced
        with a list of all possible values instead.

        Extractions with no existing .log file are skipped. If param_set_id is not None, logs without an extraction .csv
        are also skipped.

        :param param_set_id: parameter configuration used for replaying. If set to None the created EPs can only be used
            to extract logs but not replay them
        :param action_name:
        :param recording_date:
        :param log_index:
        :return: a list of ExperimentParameter objects
        """
        directory = PATH_FIELD_LOGS if param_set_id is None else PATH_LOGS_AS_CSVS
        eps = []
        if action_name is None:
            action_names = [file.name for file in directory.iterdir()]
        else:
            action_names = [action_name]
        for a_n in action_names:
            if recording_date is None:
                recording_dates = [file.name for file in (directory / a_n).iterdir()]
            else:
                recording_dates = [recording_date]
            for r_d in recording_dates:
                if log_index is None:
                    log_indices = [int(file.stem) for file in (directory / a_n / r_d).iterdir()]
                else:
                    log_indices = [log_index]
                for l_i in log_indices:
                    ep = ExperimentParameters(param_set_id=param_set_id, action_name=a_n, recording_date=r_d, log_index=l_i)
                    if ep.exists_log() and (ep.exists_extraction() or param_set_id is None):
                        eps.append(ep)
        return eps