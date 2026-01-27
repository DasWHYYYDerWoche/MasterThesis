from __future__ import annotations

from pathlib import Path
import subprocess
import time
import xml.etree.ElementTree as ET
from .FileHandler import LoggerHandler, NaoV6H25Handler, ThesisCSVReplayHandler, ThesisLogExtractionHandler
from ..Utils import PATH_SCENE, PATH_EXECUTABLE, ExtractionData



class Simulator:
    def __init__(self):
        self.MAX_INSTANCES = 5

        self._loggerHandler = LoggerHandler()
        self._naoV6H25Handler = NaoV6H25Handler()
        self._thesisCSVReplayHandler = ThesisCSVReplayHandler()
        self._thesisLogExtractionHandler = ThesisLogExtractionHandler()

    def run_log_extraction(self, extraction_datas : list[ExtractionData], scene : str, max_wait_for_ready : int = 10, max_run_duration : int = 20, num_instances : int = 1, gui : bool = True) -> bool:
        if len(extraction_datas) > self.MAX_INSTANCES:
            return False
        if max_wait_for_ready < 0 or max_run_duration < 0:
            return False
        process_list : list[subprocess.Popen[str]] = []
        process_start_time : list[float] = []
        process_ready_time : list[float] = []
        try:
            for i in range(num_instances):
                process_list.append(subprocess.Popen(str(PATH_EXECUTABLE) + " " + str(PATH_SCENE / scene) + ".ros2",
                                 stdout=subprocess.PIPE, text=True))

        except Exception as exception:
            pass

        return True
        p1,p2 = None, None
        try:
            simulator._loggerHandler.set_value("logIndex", 0)
            simulator._loggerHandler.write_to_file()
            p1 = subprocess.Popen(str(PATH_EXECUTABLE) + " " + str(PATH_SCENE / scene) + ".ros2",
                                 stdout=subprocess.PIPE, text=True)
            for line in p1.stdout:
                print(line)
                if line.strip() == "READY":
                    break
            simulator._loggerHandler.set_value("logIndex", 1)
            simulator._loggerHandler.write_to_file()
            p2 = subprocess.Popen(str(PATH_EXECUTABLE) + " " + str(PATH_SCENE / scene) + ".ros2",
                                 stdout=subprocess.PIPE, text=True)
            for line in p2.stdout:
                print(line)
                if line.strip() == "READY":
                    break
        except Exception as e:
            if isinstance(e, subprocess.TimeoutExpired):
                print("Process ran for longer than the given max_duration of " + str(max_run_duration) + " second(s)")
            else:
                print("Error during subprocess creation:\n" + str(e))
            if p1:
                p1.terminate()
            if p2:
                p2.terminate()

    def _set_log_extraction_parameters(self, extraction_data : ExtractionData):
        self._loggerHandler.set(logging=True, log_extraction=True, csv_replay=False,
                                action_name=extraction_data.action_name, log_folder=extraction_data.log_folder, log_index=extraction_data.log_index,
                                csv_name="")
        self._loggerHandler.write_to_file()
        self._thesisCSVReplayHandler


simulator = Simulator()