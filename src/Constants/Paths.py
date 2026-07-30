"""
Contains Information about the paths to different parts of the framework and log folders.
These might need to be updated when using the code on another system. Specifically the project_root folder at the bottom
"""

from __future__ import annotations
from pathlib import Path

# location of this python project
PROJECT_ROOT : Path = Path("C:/") / "Users" / "felix" / "PycharmProjects" / "Thesis" # change depending on where this project is for you
# location of the NAO framework
PATH : Path = Path.home() / "source" / "Repos"/ "NDevils2015" # on the uni pc: source/repos/pg666/NDevils2015

# path to the config of the loggerT module
PATH_CONFIG : Path = PATH / "Config"
# path to scenes
PATH_SCENE : Path = PATH_CONFIG / "Scenes"
# path to the scene used for log extraction
PATH_LOG_EXTRACTION_SCENE = PATH_SCENE / "ThesisLogExtraction"
# path to the scene used for csv replaying
PATH_CSV_REPLAY_SCENE = PATH_SCENE / "ThesisCSVReplay"
# path to the simulator logs
PATH_LOGS = PATH_CONFIG / "Logs"
# path to the simulators csv output
PATH_CSV_LOGGER = PATH_LOGS / "CSVLogger"
# path to the logs recorded on the field
PATH_FIELD_LOGS : Path = PATH_LOGS / "ThesisFieldLogs"
# path to csv files extracted from the logs
PATH_LOGS_AS_CSVS : Path = PATH_CSV_LOGGER / "logsAsCSVs"
# path to the replays of the extracted csv files
PATH_REPLAYS : Path = PATH_CSV_LOGGER / "replays"
# path to the executable
PATH_EXECUTABLE : Path = PATH / "Build" / "simulator-multiconfig" / "Release" / "SimRobot.exe"

PATH_INPUT : Path = PROJECT_ROOT / "input_files"
PATH_OUTPUT : Path = PROJECT_ROOT / "output_files"

PATH_DATASHEET_OUTPUT = PATH_OUTPUT / "motor_limits.csv"
PATH_OUTPUT_NORM_FACTORS = PATH_OUTPUT / "normalization_factors.csv"

def get_extraction_path_partial(action_name : str, recording_date : str, log_index : int) -> Path:
    return Path("logsAsCSVs") / action_name / recording_date / str(log_index)

def get_extraction_path_full(action_name : str, recording_date : str, log_index : int) -> Path:
    return PATH_CSV_LOGGER / get_extraction_path_partial(action_name, recording_date, log_index)

def get_replay_path_partial(param_set_id : str, action_name : str, recording_date : str, log_index : int) -> Path:
    return Path("replays") / ("paramSet_" + param_set_id) / action_name / recording_date / (str(log_index) + "_replayed_")

def get_replay_path_full(param_set_id : str, action_name : str, recording_date : str, log_index : int) -> Path:
    return PATH_CSV_LOGGER / get_replay_path_partial(param_set_id, action_name, recording_date, log_index)

def get_field_logs_path_partial(action_name : str, recording_date : str, log_index : int) -> Path:
    return Path("..") / "Logs" / "ThesisFieldLogs" / action_name /  recording_date / (str(log_index) + ".log")

def get_field_logs_path_full(action_name : str, recording_date : str, log_index : int) -> Path:
    return PATH_LOGS / "ThesisFieldLogs" / action_name /  recording_date / (str(log_index) + ".log")