from __future__ import annotations

from typing import override

from .FileHandler import FileHandler
from ..Constants import PATH_SCENE

class ThesisCSVReplayConHandler(FileHandler):
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
        super().__init__(PATH_SCENE / "ThesisCSVReplay.con")

    @override
    def _load_from_file(self):
        f = None
        try:
            f = open(self._path, "r")
            for line in f:
                if line.startswith("dt "):
                    value = line.split(" ", 1)[1].strip()
                    if value == "off":
                        self._data["dt"] = -1
                    else:
                        self._data["dt"] = value
                    return
            raise ValueError("dt line not found")
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
                if line.startswith("dt "):
                    value = "off" if self._data["dt"] == -1 else str(self._data["dt"])
                    lines[i] = "dt " + value + "\n"
                    f.seek(0)  # go back to start
                    f.truncate()  # remove old content
                    f.writelines(lines)
                    return
            raise ValueError("line containing dt not found")
        except Exception as e:
            raise e
        finally:
            if f is not None:
                f.close()

    @staticmethod
    @override
    def get_default() -> dict:
        return {"dt" : 113}

    def set(self, dt : int):
        self._set_value("dt", dt)