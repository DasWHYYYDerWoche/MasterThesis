from __future__ import annotations
from typing import override

from ..Constants import PATH_CONFIG
from . import  CfgHandler

class LoggerCfgHandler(CfgHandler):
    """
    File handler for the loggerT.cfg file of the simulator. Controls parameters to enable/disable logging and
    filepaths to chose where csvs are saved to and loaded from.
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__(PATH_CONFIG / "loggerT.cfg")

    @staticmethod
    @override
    def get_default() -> dict:
        return {
            'loggingActive' : False,
            'logExtractionActive' : False,
            'csvReplayActive' : False,
            'logExtractionPath' : "",
            'csvReplayPath' : "",
            'moveRobot' : False
        }

    def set(self, logging_active: bool, log_extraction_active: bool, csv_replay_active: bool,
            log_extraction_path: str, csv_replay_path: str, move_robot : bool):
        self._set_values(keys=list(self.get_default().keys()),
                         values=[logging_active, log_extraction_active, csv_replay_active,
                                 log_extraction_path, csv_replay_path, move_robot])

    def set_extract(self, log_extraction_folder_name: str):
        self.set(logging_active=True, log_extraction_active=True, csv_replay_active=False,
                 log_extraction_path=log_extraction_folder_name, csv_replay_path="", move_robot=False)

    def set_replay(self, log_extraction_folder_name : str, csv_replay_folder_name: str, move_robot : bool):
        self.set(logging_active=True, log_extraction_active=False, csv_replay_active=True,
                 log_extraction_path=log_extraction_folder_name, csv_replay_path=csv_replay_folder_name, move_robot=move_robot)