from __future__ import annotations

from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

PATH : Path = Path.home() / "source" / "repos" / "NDevils2015"
# path to the config of the loggerT module
PATH_LOGGER_CFG : Path = PATH / "Config" / "loggerT.cfg"
# path to the logs recorded on the field
PATH_FIELD_LOGS : Path = PATH / "Config" / "Logs" / "ThesisFieldLogs"
# path to csv files extracted from the logs
PATH_LOGS_AS_CSVS : Path = PATH / "Config" / "Logs" / "CSVLogger" / "logsAsCSVs"
# path to the replays of the extracted csv files
PATH_REPLAYS : Path = PATH / "Config" / "Logs" / "CSVLogger" / "replays"
# path to the executable
PATH_EXECUTABLE : Path = PATH / "Build" / "simulator-multiconfig" / "Release" / "SimRobot.exe"
# path to scenes
PATH_SCENE : Path = PATH / "Config" / "Scenes"

HINGE_NAMES = [
"HeadYaw","HeadPitch",
"LShoulderPitch","LShoulderRoll","LElbowYaw","LElbowRoll","LWristYaw",
"RShoulderPitch","RShoulderRoll","RElbowYaw","RElbowRoll","RWristYaw",
"LHipYawPitch","LHipRoll","LHipPitch","LKneePitch","LAnklePitch","LAnkleRoll",
"RHipYawPitch","RHipRoll","RHipPitch","RKneePitch","RAnklePitch","RAnkleRoll"
]

class Simulator:
    def __init__(self):
        self._replay_scene = ET.parse(PATH_SCENE / "ThesisCSVReplay.ros2")
        self._nao_config = ET.parse(PATH_SCENE / "Includes" / "NaoV6H25.rsi2")
        self._nao_config_backup = ET.parse(PATH_SCENE / "Includes" / "NaoV6H25_BACKUP.rsi2")

    def run_extraction(self, action_name : str, log_folder : str, log_index : int, csv_name : str):
        self.set_logger_cfg_extract(action_name, log_folder, log_index, csv_name)
        self.run("ThesisLogExtraction", 5, 1)

    def run_replay(self, action_name : str, log_folder : str, log_index : int, csv_name : str):
        self.set_logger_cfg_replay(action_name, log_folder, log_index, csv_name)
        self.run("ThesisCSVReplay", 5, 1)

    def run(self, scene : str, max_duration : int, num_instances : int):
        try:
            p = subprocess.Popen(str(PATH_EXECUTABLE) + " " + str(PATH_SCENE / scene) + ".ros2",
                                 stdout=subprocess.PIPE, text=True)
            for line in p.stdout:
                print(line)
                if line.strip() == "READY":
                    break
            p.wait(max_duration)
        except Exception as e:
            if isinstance(e, subprocess.TimeoutExpired):
                print("Process ran for longer than the given max_duration of " + str(max_duration) + " second(s)")
            else:
                print("Error during subprocess creation:\n" + str(e))
            if p:
                p.terminate()

    # ---------- logger config modification

    def set_logger_cfg_none(self):
        self._set_logger_cfg(logging=False, log_extraction=False, csv_replay=False, action_name="", log_folder="", log_index=-1,csv_name="")

    def set_logger_cfg_extract(self, action_name : str, log_folder : str, log_index : int, csv_name : str):
        self._set_logger_cfg(logging=True, log_extraction=True, csv_replay=False, action_name=action_name, log_folder=log_folder, log_index=log_index,csv_name=csv_name)

    def set_logger_cfg_replay(self, action_name : str, log_folder : str, log_index : int, csv_name : str):
        self._set_logger_cfg(logging=True, log_extraction=False, csv_replay=True, action_name=action_name, log_folder=log_folder, log_index=log_index,csv_name=csv_name)

    def _set_logger_cfg(self, logging : bool, log_extraction : bool, csv_replay : bool, action_name : str, log_folder : str, log_index : int, csv_name : str):
        text = ""
        text += "logging = " + str(logging).lower() + ";\n"
        text += "logExtraction = " + str(log_extraction).lower() + ";\n"
        text += "csvReplay = " + str(csv_replay).lower() + ";\n"
        text += "actionName = \"" + action_name + "\";\n"
        text += "logFolder = \"" + log_folder + "\";\n"
        text += "logIndex = " + str(log_index) + ";\n"
        text += "csvName = \"" + csv_name + "\";\n"
        with open(PATH_LOGGER_CFG, "w") as f:
            f.write(text)

    # ---------- ThesisLogExtraction scene modification

    def _set_log_extraction_con_none(self):
        path = PATH_SCENE / "ThesisLogExtraction.con"
        lines = ""
        with open(path, "r") as f:
            lines = f.readlines()
        # change text
        with open(path, "w") as f:
            f.write("sl LOG ${Logfile:,../Logs/*Combined.log}\n")
            for line in lines:
                if not line.startswith("sl LOG "):
                    f.write(line)

    def _set_log_extraction_con(self, action_name :str, log_recording_date : str, log_index : int):
        path = PATH_SCENE / "ThesisLogExtraction.con"
        lines = ""
        with open(path, "r") as f:
            lines = f.readlines()
        # change text
        with open(path, "w") as f:
            f.write("sl LOG ../log/ThesisFieldLogs/" + action_name + "/" + log_recording_date + "/" + str(log_index) + ".log" + "\n")
            for line in lines:
                if not line.startswith("sl LOG "):
                    f.write(line)

    # ---------- replay scene modification

    def _reset_replay_scene_parameters(self):
        self._set_replay_scene_parameters(kp=12500, kd=10000, contact_kp=1425, contact_kd=7.5)

    def _set_replay_scene_parameters(self, kp : float, kd : float, contact_kp : float, contact_kd : float):
        element = self._replay_scene.getroot().find("Scene")
        element.set("Kp",str(kp))
        element.set("Kd",str(kd))
        element.set("contactKp",str(contact_kp))
        element.set("ContactKd",str(contact_kd))
        self._replay_scene.write(PATH_SCENE / "ThesisCSVReplay.ros2")

    # ---------- nao config modification

    def _reset_nao_rsi2(self):
        hinges = [hinge.find("Axis").find("ServoMotor") for hinge in list(self._nao_config.getroot().iter("Hinge"))]
        defaults = [hinge.find("Axis").find("ServoMotor") for hinge in list(self._nao_config_backup.getroot().iter("Hinge"))]
        for hinge, default in zip(hinges, defaults):
            for attribute in default.keys():
                hinge.set(attribute, default.get(attribute))

    def _set_nao_rsi2(self):
        r = self._nao_config.getroot()
        for hinge in r.iter("Hinge"):
            print(hinge.get("name"))




class ReplayScene:
    def __init__(self):
        pass




class Hinge:
    def __init__(self, max_velocity : float, max_force : float, p : float, i : float, d : float):
        self._max_velocity = max_velocity
        self._max_force = max_force
        self._p = p
        self._i = i
        self._d = d

    @property
    def max_velocity(self) -> float:
        return self._max_velocity

    @property
    def max_force(self) -> float:
        return self._max_force

    @property
    def p(self) -> float:
        return self._p

    @property
    def i(self) -> float:
        return self._i

    @property
    def d(self) -> float:
        return self._d

    @max_velocity.setter
    def max_velocity(self, value: float) -> None:
        self._max_velocity = value

    @max_force.setter
    def max_force(self, value: float) -> None:
        self._max_force = value

    @p.setter
    def p(self, value: float) -> None:
        self._p = value

    @i.setter
    def i(self, value: float) -> None:
        self._i = value

    @d.setter
    def d(self, value: float) -> None:
        self._d = value