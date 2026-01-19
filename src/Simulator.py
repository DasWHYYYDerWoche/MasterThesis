from __future__ import annotations
from pathlib import Path
import subprocess

class Simulator:
    def __init__(self):
        self._PATH : Path = Path.home() / "source" / "repos" / "NDevils2015"
        # path to the config of the loggerT module
        self._PATH_LOGGER_CONFIG : Path = self._PATH / "Config" / "loggerT.cfg"
        # path to the logs recorded on the field
        self._PATH_FIELD_LOGS : Path = self._PATH / "Config" / "Logs" / "ThesisFieldLogs"
        # path to csv files extracted from the logs
        self._PATH_LOGS_AS_CSVS : Path = self._PATH / "Config" / "Logs" / "CSVLogger" / "logsAsCSVs"
        # path to the replays of the extracted csv files
        self._PATH_REPLAYS : Path = self._PATH / "Config" / "Logs" / "CSVLogger" / "replays"
        # path to the executable
        self._PATH_EXECUTABLE : Path = self._PATH / "Build" / "simulator-multiconfig" / "Release" / "SimRobot.exe"
        # path to scenes
        self._PATH_SCENE : Path = self._PATH / "Config" / "Scenes"


    def run_extraction(self, action_name : str, log_folder : str, log_index : int, csv_name : str):
        self.set_logger_cfg_extract(action_name, log_folder, log_index, csv_name)
        self.run("ThesisLogExtraction", 5)

    def run_replay(self, action_name : str, log_folder : str, log_index : int, csv_name : str):
        self.set_logger_cfg_replay(action_name, log_folder, log_index, csv_name)
        self.run("ThesisCSVReplay", 5)

    def run(self, scene : str, max_duration : int):
        try:
            p = subprocess.Popen(str(self._PATH_EXECUTABLE) + " " + str(self._PATH_SCENE / scene) + ".ros2")
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
        with open(self._PATH_LOGGER_CONFIG, "w") as f:
            f.write(text)

    # ---------- ThesisLogExtraction scene modification

    def _set_log_extraction_con_none(self):
        path = self._PATH_SCENE / "ThesisLogExtraction.con"
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
        path = self._PATH_SCENE / "ThesisLogExtraction.con"
        lines = ""
        with open(path, "r") as f:
            lines = f.readlines()
        # change text
        with open(path, "w") as f:
            f.write("sl LOG ../log/ThesisFieldLogs/" + action_name + "/" + log_recording_date + "/" + str(log_index) + ".log" + "\n")
            for line in lines:
                if not line.startswith("sl LOG "):
                    f.write(line)

    # ---------- Properties

    @property
    def path(self) -> Path:
        return self._PATH

    @property
    def path_logger_config(self) -> Path:
        return self._PATH_LOGGER_CONFIG

    @property
    def path_field_logs(self) -> Path:
        return self._PATH_FIELD_LOGS

    @property
    def path_logs_as_csvs(self) -> Path:
        return self._PATH_LOGS_AS_CSVS

    @property
    def path_replays(self) -> Path:
        return self._PATH_REPLAYS

    @property
    def path_executable(self) -> Path:
        return self._PATH_EXECUTABLE

    @property
    def path_scene(self) -> Path:
        return self._PATH_SCENE