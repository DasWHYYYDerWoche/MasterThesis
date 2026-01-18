from .core import LOGS_REPLAY_PATH, LOGS_FIELD_PATH
import pathlib

class ExperimentData:
    def __init__(self, name : str):
        self._name = name

    def get_field_log_path(self) -> pathlib.Path:
        return LOGS_FIELD_PATH / self._name

    def get_replay_log_path(self) -> pathlib.Path:
        return LOGS_REPLAY_PATH / self._name

KICK : ExperimentData = ExperimentData("kick")
WALK : ExperimentData = ExperimentData("walk")
TURN : ExperimentData = ExperimentData("turn")
SIDESTEP : ExperimentData = ExperimentData("sidestep")
STANDUP_FRONT : ExperimentData = ExperimentData("standup_front")
STANDUP_BACK : ExperimentData = ExperimentData("standup_back")