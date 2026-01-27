from __future__ import annotations
from .FileHandler import  FileHandler
from ...Utils import PATH_SCENE

class ThesisLogExtractionHandler(FileHandler):
    def __init__(self):
        super().__init__(PATH_SCENE / "ThesisLogExtraction.con")


    def _load(self):
        with open(self._path, "r") as f:
            for line in f:
                if line.startswith("sl LOG"):
                    self._data["path"] = line.split("sl LOG", 1)[1]
                    return

    def get_default(self) -> dict:
        return {"path" : "${Logfile:,../Logs/*Combined.log}"}

    def _write_to_file(self):
        lines = []
        with open(self._path, "r") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("sl LOG"):
                lines[i] = "sl LOG " + self._data["path"] + "\n"
        with open(self._path, "w") as f:
            f.writelines(lines)


    def set(self, path : str):
        self.set_value("path", path)


"""sl LOG ${Logfile:,../Logs/*Combined.log}

call ReplayRobot

dr representation:JointRequest
dr representation:JointSensorData
dr representation:InertialSensorData
dr representation:SystemSensorData
dr representation:FsrSensorData
dr representation:KeyStates

dt 113

log start"""