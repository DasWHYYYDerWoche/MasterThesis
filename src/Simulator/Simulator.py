from __future__ import annotations

from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from .FileHandler import LoggerHandler, NaoV6H25Handler, ThesisCSVReplayHandler
from ..Utils import PATH_SCENE, PATH_EXECUTABLE



class Simulator:
    def __init__(self):
        self._replay_scene = ET.parse(PATH_SCENE / "ThesisCSVReplay.ros2")
        self._nao_config = ET.parse(PATH_SCENE / "Includes" / "NaoV6H25.rsi2")
        self._nao_config_backup = ET.parse(PATH_SCENE / "Includes" / "NaoV6H25_BACKUP.rsi2")

        self._loggerHandler = LoggerHandler()
        self._naoV6H25Handler = NaoV6H25Handler()
        self._thesisCSVReplayHandler = ThesisCSVReplayHandler()

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

simulator = Simulator()