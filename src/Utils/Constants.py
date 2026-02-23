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

HINGE_NAMES = [
"headYaw","headPitch",
"lShoulderPitch","lShoulderRoll","lElbowYaw","lElbowRoll","lWristYaw",
"rShoulderPitch","rShoulderRoll","rElbowYaw","rElbowRoll","rWristYaw",
"lHipYawPitch","lHipRoll","lHipPitch","lKneePitch","lAnklePitch","lAnkleRoll",
"rHipYawPitch","rHipRoll","rHipPitch","rKneePitch","rAnklePitch","rAnkleRoll",
]

JOINT_DEFLECTIONS = {
    # Head
    "headYaw": (-119.5, 119.5),
    "headPitch": (-38.5, 29.5),

    # Left Arm
    "lShoulderPitch": (-119.5, 119.5),
    "lShoulderRoll": (-18.0, 76.0),
    "lElbowYaw": (-119.5, 119.5),
    "lElbowRoll": (-88.5, -2.0),
    "lWristYaw": (-104.5, 104.5),
    "lHand" : (0,1),

    # Right Arm
    "rShoulderPitch": (-119.5, 119.5),
    "rShoulderRoll": (-76.0, 18.0),
    "rElbowYaw": (-119.5, 119.5),
    "rElbowRoll": (2.0, 88.5),
    "rWristYaw": (-104.5, 104.5),
    "rHand" : (0,1),

    # Left Leg
    "lHipYawPitch": (-65.62, 42.44),
    "lHipRoll": (-21.74, 45.29),
    "lHipPitch": (-88.0, 27.73),
    "lKneePitch": (-5.29, 121.04),
    "lAnklePitch": (-68.15, 52.86),
    "lAnkleRoll": (-22.79, 44.06),

    # Right Leg
    "rHipYawPitch": (-65.62, 42.44),
    "rHipRoll": (-45.29, 21.74),
    "rHipPitch": (-88.0, 27.73),
    "rKneePitch": (-5.90, 121.47),
    "rAnklePitch": (-67.97, 53.40),
    "rAnkleRoll": (-44.06, 22.80),
}

JOINT_RANGES = {key : abs(value[0] - value[1]) for key, value in JOINT_DEFLECTIONS.items()}

def get_extraction_path_partial(action_name : str, recording_date : str, log_index : int) -> Path:
    return Path("logsAsCSVs") / action_name / recording_date / str(log_index)

def get_extraction_path_full(action_name : str, recording_date : str, log_index : int) -> Path:
    return PATH_CSV_LOGGER / get_extraction_path_partial(action_name, recording_date, log_index)

def get_replay_path_partial(param_set_id : str, action_name : str, recording_date : str, log_index : int, replay_date : str) -> Path:
    return Path("replays") / ("paramSet_" + param_set_id) / action_name / recording_date / (str(log_index) + "_replayed_" + replay_date)

def get_replay_path_full(param_set_id : str, action_name : str, recording_date : str, log_index : int, replay_date : str) -> Path:
    return PATH_CSV_LOGGER / get_replay_path_partial(param_set_id, action_name, recording_date, log_index, replay_date)

def get_field_logs_path(action_name : str, recording_date : str, log_index : int) -> Path:
    return Path("..") / "Logs" / "ThesisFieldLogs"/ action_name /  recording_date / (str(log_index) + ".log")