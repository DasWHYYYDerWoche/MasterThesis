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
"lShoulderPitch","lShoulderRoll","lElbowYaw","lElbowRoll","lWristYaw","lHand",
"rShoulderPitch","rShoulderRoll","rElbowYaw","rElbowRoll","rWristYaw","rHand",
"lHipYawPitch","lHipRoll","lHipPitch","lKneePitch","lAnklePitch","lAnkleRoll",
"rHipYawPitch","rHipRoll","rHipPitch","rKneePitch","rAnklePitch","rAnkleRoll",
]

JOINT_DEFLECTIONS = {
    # Head
    "HeadYaw": (-119.5, 119.5),
    "HeadPitch": (-38.5, 29.5),

    # Left Arm
    "LShoulderPitch": (-119.5, 119.5),
    "LShoulderRoll": (-18.0, 76.0),
    "LElbowYaw": (-119.5, 119.5),
    "LElbowRoll": (-88.5, -2.0),
    "LWristYaw": (-104.5, 104.5),

    # Right Arm
    "RShoulderPitch": (-119.5, 119.5),
    "RShoulderRoll": (-76.0, 18.0),
    "RElbowYaw": (-119.5, 119.5),
    "RElbowRoll": (2.0, 88.5),
    "RWristYaw": (-104.5, 104.5),

    # Left Leg
    "LHipYawPitch": (-65.62, 42.44),
    "LHipRoll": (-21.74, 45.29),
    "LHipPitch": (-88.0, 27.73),
    "LKneePitch": (-5.29, 121.04),
    "LAnklePitch": (-68.15, 52.86),
    "LAnkleRoll": (-22.79, 44.06),

    # Right Leg
    "RHipYawPitch": (-65.62, 42.44),
    "RHipRoll": (-45.29, 21.74),
    "RHipPitch": (-88.0, 27.73),
    "RKneePitch": (-5.90, 121.47),
    "RAnklePitch": (-67.97, 53.40),
    "RAnkleRoll": (-44.06, 22.80),
}

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