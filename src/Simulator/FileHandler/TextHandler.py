from __future__ import annotations
from .FileHandler import  FileHandler
from ...Utils import PATH_SCENE

import logging
logger = logging.getLogger("global_logger")

class ThesisLogExtractionHandler(FileHandler):
    def __init__(self):
        super().__init__(PATH_SCENE / "ThesisLogExtraction.con")

    def _load_from_file(self):
        f = None
        try:
            f = open(self._path, "r")
            for line in f:
                if line.startswith("sl LOG"):
                    self._data["path"] = line.split("sl LOG", 1)[1]
                    logger.debug("%s loaded from %s", type(self).__name__, self._path)
                    f.close()
                    return
            raise ValueError("sl LOG line not found")
        except Exception as e:
            logger.exception("%s failed to load due to %s", type(self).__name__, type(e).__name__)
        finally:
            if f is not None:
                f.close()

    def get_default(self) -> dict:
        return {"path" : "${Logfile:,../Logs/*Combined.log}"}

    def write_to_file(self):
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
                    logger.debug("%s wrote data to file %s", type(self).__name__, self._path)
                    return
            raise ValueError("sl LOG line not found")
        except Exception as e:
            logger.exception("%s failed to write due to %s", type(self).__name__, type(e).__name__)
        finally:
            if f is not None:
                f.close()

    def set(self, path : str):
        self.set_value("path", path)