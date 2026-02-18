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
        self._initial_data: dict = {}
        self.load_from_file()

    @abstractmethod
    def _load_from_file(self):
        pass

    @abstractmethod
    def _write_to_file(self):
        pass

    def load_from_file(self):
        try:
            self._load_from_file()
            if len(self._data.keys()) is not len(self.get_default().keys()):
                raise ValueError("Inconsistent number of keys")
            self._initial_data = self._data.copy()
            logger.info("%s loaded from %s", type(self).__name__, self._path)
        except Exception as e:
            logger.exception("%s failed to load due to %s", type(self).__name__, type(e).__name__)

    def write_to_file(self):
        try:
            self._write_to_file()
            logger.info("%s written to %s", type(self).__name__, self._path)
        except Exception as e:
            logger.exception("%s failed to write due to %s", type(self).__name__, type(e).__name__)

    @staticmethod
    @abstractmethod
    def get_default() -> dict:
        pass

    def _set_value(self, key: str, value: Any):
        if self._data.keys().__contains__(key):
            self._data[key] = value
            logger.debug("%s set \"%s\" to \"%s\"", type(self).__name__, key, value)
        else:
            logger.warning("%s does not contain key \"%s\"", type(self).__name__, key)

    def _set_values(self, keys: list[str], values: list[Any]):
        if len(keys) != len(values):
            logger.debug("%s values \"%s\" and keys \"%s\" have different length", type(self).__name__, keys, values)
            return
        contained_keys = []
        contained_values = []
        not_contained_keys = []
        for key, value in zip(keys, values):
            if key in self._data.keys():
                self._data[key] = value
                contained_keys.append(key)
                contained_values.append(value)
            else:
                not_contained_keys.append(key)
        if len(contained_keys) > 0:
            logger.debug("%s set \"%s\" to \"%s\"", type(self).__name__, contained_keys, contained_values)
        if len(not_contained_keys) > 0:
            logger.warning("%s does not contain key(s) \"%s\"", type(self).__name__, not_contained_keys)

    def set_default(self):
        logger.debug("%s set to default", type(self).__name__)
        default = self.get_default()
        self._set_values(list(default.keys()), list(default.values()))

    def set_to_initial_values(self):
        logger.debug("%s set to initial values", type(self).__name__)
        self._data = self._initial_data.copy()

    @property
    def keys(self) -> list[str]:
        return list(self._data.keys())

    @property
    def values(self) -> list[Any]:
        return list(self._data.values())