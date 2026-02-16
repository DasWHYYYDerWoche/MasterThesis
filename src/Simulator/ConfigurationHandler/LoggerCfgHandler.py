from __future__ import annotations
from typing import override

from ...Utils import  CfgHandler, PATH_CONFIG

class LoggerCfgHandler(CfgHandler):

    def __init__(self):
        super().__init__(PATH_CONFIG / "loggerT.cfg")

    @staticmethod
    @override
    def get_default() -> dict:
        return {
            'loggingActive' : False,
            'logExtractionActive' : False,
            'csvReplayActive' : False,
            'logExtractionPath' : "",
            'csvReplayPath' : ""
        }

    def set(self, logging_active: bool, log_extraction_active: bool, csv_replay_active: bool,
            log_extraction_path: str, csv_replay_path: str):
        self._set_values(keys=list(self.get_default().keys()),
                         values=[logging_active, log_extraction_active, csv_replay_active,
                                 log_extraction_path, csv_replay_path])

    def set_extract(self, log_extraction_folder_name: str):
        self.set(logging_active=True, log_extraction_active=True, csv_replay_active=False,
                 log_extraction_path=log_extraction_folder_name, csv_replay_path="")

    def set_replay(self, log_extraction_folder_name : str, csv_replay_folder_name: str):
        self.set(logging_active=True, log_extraction_active=False, csv_replay_active=True,
                 log_extraction_path=log_extraction_folder_name, csv_replay_path=csv_replay_folder_name)