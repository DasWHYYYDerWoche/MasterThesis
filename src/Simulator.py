from __future__ import annotations
import pathlib
import subprocess
import fileinput


class Simulator:
    def __init__(self):
        self._PATH : pathlib.Path = pathlib.Path.home() / "source" / "repos" / "NDevils2015"
        # path to the config of the loggerT module
        self._PATH_LOGGER_CONFIG : pathlib.Path = self._PATH / "Config" / "loggerT.cfg"
        # path to the logs recorded on the field
        self._PATH_FIELD_LOGS : pathlib.Path = self._PATH / "Config" / "Logs" / "ThesisFieldLogs"
        # path to csv files extracted from the logs
        self._PATH_LOGS_AS_CSVS : pathlib.Path = self._PATH / "Config" / "Logs" / "CSVLogger" / "logsAsCSVs"
        # path to the replays of the extracted csv files
        self._PATH_REPLAYS : pathlib.Path = self._PATH / "Config" / "Logs" / "CSVLogger" / "replays"
        # path to the executable
        self._PATH_EXECUTABLE : pathlib.Path = self._PATH / "Build" / "simulator-multiconfig" / "Release" / "SimRobot.exe"
        # path to scenes
        self._PATH_SCENE : pathlib.Path = self._PATH / "Config" / "Scenes"


    def run_extraction(self, action_name : str, log_folder : str, log_index : int, csv_name : str):
        self.set_logger_cfg_extract(action_name, log_folder, log_index, csv_name)
        self.run("ThesisLogExtraction", 5)

    def run_replay(self, action_name : str, log_folder : str, log_index : int, csv_name : str):
        self.set_logger_cfg_replay(action_name, log_folder, log_index, csv_name)
        self.run("ThesisCSVReplay", 5)

    def run(self, scene : str, max_duration : int):
        try:
            p = subprocess.Popen( str(self._PATH_EXECUTABLE) + " " + str(self._PATH_SCENE / scene) + ".ros2")
            p.wait()
        except Exception as e:
            raise e

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
        print(lines)
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
        print(lines)
        with open(path, "w") as f:
            f.write("sl LOG ../log/ThesisFieldLogs/" + action_name + "/" + log_recording_date + "/" + str(log_index) + ".log" + "\n")
            for line in lines:
                if not line.startswith("sl LOG "):
                    f.write(line)


    @staticmethod
    def _update_file(path: pathlib.Path, replacement: list[tuple[str, str]]) -> bool:
        file_text = ""

        with open(path, "r") as f:
            file_text = f.read()
        # change text
        for (old, new) in replacement:
            file_text = file_text.replace(old, new)
        with open(path, "w") as f:
            f.write(file_text)
        return True