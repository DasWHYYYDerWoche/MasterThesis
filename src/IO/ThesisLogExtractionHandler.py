from __future__ import annotations

from typing import override

from .FileHandler import FileHandler
from ..Constants import PATH_SCENE

class ThesisLogExtractionHandler(FileHandler):
    """
    File handler for the ThesisLogExtraction.con file of the simulator. Used to set the log path during log extraction.
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        super().__init__(PATH_SCENE / "ThesisLogExtraction.con")

    @override
    def _load_from_file(self):
        f = None
        try:
            f = open(self._path, "r")
            for line in f:
                if line.startswith("sl LOG"):
                    self._data["path"] = line.split("sl LOG", 1)[1]
                    return
            raise ValueError("sl LOG line not found")
        except Exception as e:
            raise e
        finally:
            if f is not None:
                f.close()

    @override
    def _write_to_file(self):
        f = None
        try:
            f = open(self._path, "r+")
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("sl LOG"):
                    lines[i] = "sl LOG " + self._data["path"] + "\n"
                    f.seek(0)  # go back to start
                    f.truncate()  # remove old content
                    f.writelines(lines)
                    return
            raise ValueError("line containing sl LOG not found")
        except Exception as e:
            raise e
        finally:
            if f is not None:
                f.close()

    @staticmethod
    @override
    def get_default() -> dict:
        return {"path" : "${Logfile:,../Logs/*Combined.log}"}

    def set(self, path : str):
        self._set_value("path", path)