from __future__ import annotations
from pathlib import Path
from typing import Optional

from ..Simulator import Simulator
from..Utils import PATH_FIELD_LOGS, PATH_LOGS_AS_CSVS, ExtractionData, ACTIONS

class LogExtractor:
    def __init__(self, batch_size : int = 5):
        simulator : Simulator = Simulator()
        self._batch_size : int = batch_size

    def _run(self, extraction_datas : list[ExtractionData]):
        pass

    def extract(self, action_name : Optional[str] = None, date : Optional[str] = None, log_index : Optional[int] = None):
        eds = LogExtractor._get_log_files(action_name, date, log_index)



    @staticmethod
    def _get_log_files(action_name : Optional[str] = None, date : Optional[str] = None, log_index : Optional[int] = None) -> list[ExtractionData]:
        if action_name is None:
            if date is None:
                return LogExtractor._get_ed_all()
            else:
                return LogExtractor._get_ed_date(date)
        if date is None:
            return LogExtractor._get_ed_action(action_name)
        if log_index is None:
            return LogExtractor._get_ed_action_date(action_name, date)
        return [ExtractionData(action_name, date, log_index)]

    @staticmethod
    def _get_ed_all() -> list[ExtractionData]:
        eds = []
        for action_name in ACTIONS:
            eds.extend(LogExtractor._get_ed_action(action_name))
        return eds

    @staticmethod
    def _get_ed_date(date : str):
        eds = []
        for action_name in ACTIONS:
            for file in (PATH_FIELD_LOGS / action_name / date).iterdir():
                eds.append(ExtractionData(action_name, date, int(file.stem)))
        return eds

    @staticmethod
    def _get_ed_action(action_name : str) -> list[ExtractionData]:
        eds = []
        for file in (PATH_FIELD_LOGS / action_name).iterdir():
            eds.extend(LogExtractor._get_ed_action_date(action_name, file.name))
        return eds

    @staticmethod
    def _get_ed_action_date(action_name : str, date : str) -> list[ExtractionData]:
        eds = []
        for file in (PATH_FIELD_LOGS / action_name / date).iterdir():
            if file.suffix == ".log":
              eds.append(ExtractionData(action_name, date, int(file.stem)))
        return eds