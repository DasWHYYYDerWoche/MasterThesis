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
            'loggingMode' : -1,
            'logExtractionPath' : "",
            'csvReplayPath' : "",
            'moveRobot' : -1,
            'recordingDuration' : -1
        }

    def set(self, logging_mode : int,
            log_extraction_path: str, csv_replay_path: str, move_robot : int, recording_duration : int):
        self._set_values(keys=list(self.get_default().keys()),
                         values=[logging_mode,
                                 log_extraction_path, csv_replay_path, move_robot, recording_duration])

    def set_extract(self, log_extraction_folder_name: str, recording_duration : int):
        self.set(logging_mode=0,
                 log_extraction_path=log_extraction_folder_name, csv_replay_path="", move_robot=-1, recording_duration = recording_duration)

    def set_replay(self, log_extraction_folder_name : str, csv_replay_folder_name: str, move_robot : int, recording_duration : int):
        self.set(logging_mode=1,
                 log_extraction_path=log_extraction_folder_name, csv_replay_path=csv_replay_folder_name, move_robot=move_robot, recording_duration = recording_duration)