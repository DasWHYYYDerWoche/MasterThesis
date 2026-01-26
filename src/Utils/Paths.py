from __future__ import annotations
from pathlib import Path

PATH : Path = Path.home() / "source" / "repos" / "NDevils2015"
# path to the config of the loggerT module
PATH_CONFIG : Path = PATH / "Config"
# path to scenes
PATH_SCENE : Path = PATH_CONFIG / "Scenes"
# path to the logs recorded on the field
PATH_FIELD_LOGS : Path = PATH_CONFIG / "Logs" / "ThesisFieldLogs"
# path to csv files extracted from the logs
PATH_LOGS_AS_CSVS : Path = PATH_CONFIG / "Logs" / "CSVLogger" / "logsAsCSVs"
# path to the replays of the extracted csv files
PATH_REPLAYS : Path = PATH_CONFIG / "Logs" / "CSVLogger" / "replays"
# path to the executable
PATH_EXECUTABLE : Path = PATH / "Build" / "simulator-multiconfig" / "Release" / "SimRobot.exe"