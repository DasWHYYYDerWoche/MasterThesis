from __future__ import annotations


class ExperimentData:
    def __init__(self, logging : bool = False, log_extraction : bool = False, csv_replay : bool = False, action_name : str = "", parameter_set : str = "", recording_date : str = "", log_index : int = -1, csv_name : str = ""):
        self._logging: bool = logging
        self._log_extraction: bool = log_extraction
        self._csv_replay: bool = csv_replay
        self._action_name: str = action_name
        self._parameter_set: str = parameter_set
        self._recording_date: str = recording_date
        self._log_index: int = log_index
        self._csv_name: str = csv_name

    @staticmethod
    def get_extraction_data(action_name : str, recording_date : str, log_index : int):
        return ExperimentData(logging = True, log_extraction=True, action_name=action_name, recording_date=recording_date, log_index=log_index)

    @staticmethod
    def get_replay_data(action_name : str, parameter_set : str, recording_date : str, log_index : int, csv_name : str):
        return ExperimentData(logging = True, csv_replay=True, action_name=action_name, parameter_set=parameter_set, recording_date=recording_date, log_index=log_index, csv_name=csv_name)

    @property
    def logging(self) -> bool:
        return self._logging

    @property
    def log_extraction(self) -> bool:
        return self._log_extraction

    @property
    def csv_replay(self) -> bool:
        return self._csv_replay

    @property
    def action_name(self) -> str:
        return self._action_name

    @property
    def parameter_set(self) -> str:
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
        if not self._logging:
            return "ExperimentData: [logging = False]"
        if self._log_extraction and not self._csv_replay:
            return "ExtractionData: [" + self._action_name + "," + self._recording_date + "," + str(self.log_index) + "]"
        if self._csv_replay and not self._log_extraction:
            return "ReplayData: [" + self._action_name + "," + self._parameter_set + "," + self._recording_date + "," + str(self.log_index) + "," + self._csv_name + "]"
        return "ShittyData"