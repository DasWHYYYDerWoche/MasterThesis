from __future__ import annotations
from pathlib import Path

PATH : Path = Path.home() / "source" / "repos" / "NDevils2015"
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


ACTION_NAMES = [action_folder.name for action_folder in PATH_FIELD_LOGS.iterdir()]