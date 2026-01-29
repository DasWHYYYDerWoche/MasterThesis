from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import logging
logger = logging.getLogger("global_logger")

class FileHandler(ABC):
    def __init__(self, path: Path):
        self._path = path
        self._data: dict = {}
        self._load_from_file()

    @abstractmethod
    def _load_from_file(self):
        pass

    @abstractmethod
    def get_default(self) -> dict:
        pass

    @abstractmethod
    def write_to_file(self):
        pass

    def set_value(self, key: str, value: Any):
        logger.debug("%s set \"%s\" to \"%s\"", type(self).__name__, key, value)
        self._data[key] = value

    def set_values(self, keys: list[str], values: list[Any]):
        if len(keys) != len(values):
            logger.debug("%s values \"%s\" and keys \"%s\" have different length", type(self).__name__, keys, values)
            return False
        logger.debug("%s set \"%s\" to \"%s\"", type(self).__name__, keys, values)
        for key, value in zip(keys, values):
            self._data[key] = value
        return True

    def set_default(self):
        logger.debug("%s set to default", type(self).__name__)
        default = self.get_default()
        self.set_values(list(default.keys()), list(default.values()))

    @property
    def keys(self) -> list[str]:
        return list(self._data.keys())

    @property
    def values(self) -> list[Any]:
        return list(self._data.values())