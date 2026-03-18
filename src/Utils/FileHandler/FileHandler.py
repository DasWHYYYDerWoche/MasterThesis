from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import logging
logger = logging.getLogger("global_logger")

class FileHandler(ABC):
    """
    superclass to handle all config read and write operations done by the simulator.
    Provides error handling and a consistent
    """
    def __init__(self, path: Path):
        self._path = path
        self._data: dict = {}
        self._initial_data: dict = {}
        self.load_from_file()


    @staticmethod
    @abstractmethod
    def get_default() -> dict:
        pass

    @abstractmethod
    def _load_from_file(self):
        """
        Load data from file into the _data variable.
        Implementation does not need error handling.
        """
        pass

    @abstractmethod
    def _write_to_file(self):
        """
        Write data from _data to file.
        Implementation does not need error handling.
        """
        pass

    def load_from_file(self):
        """
        load _data from file into the _data parameters.
        Additionally, fills the _initial_data parameter with a shallow copy of _data.
        """
        try:
            self._load_from_file()
            if len(self._data.keys()) is not len(self.get_default().keys()):
                raise ValueError("Inconsistent number of keys")
            self._initial_data = self._data.copy()
            logger.info("%s loaded from %s", type(self).__name__, self._path)
        except Exception as e:
            logger.exception("%s failed to load due to %s", type(self).__name__, type(e).__name__)

    def write_to_file(self):
        """
        Write _data object to file.
        """
        try:
            self._write_to_file()
            logger.info("%s written to %s", type(self).__name__, self._path)
        except Exception as e:
            logger.exception("%s failed to write due to %s", type(self).__name__, type(e).__name__)

    def _set_value(self, key: str, value: Any) -> bool:
        """
        Sets the given key to the given value.
        If the key does not exist, nothing happens.
        :param key:
        :param value:
        :return: True if the key exited, False otherwise
        """
        if self._data.keys().__contains__(key):
            self._data[key] = value
            logger.debug("%s set \"%s\" to \"%s\"", type(self).__name__, key, value)
            return True
        else:
            logger.warning("%s does not contain key \"%s\"", type(self).__name__, key)
            return False

    def _set_values(self, keys: list[str], values: list[Any]):
        """
        Sets the value of each key in the keys list to the corresponding value in the values list.
        Keys that don't exist are ignored.
        :param keys:
        :param values:
        :return:
        """
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
        """
        Sets the _data object to the dict returned by get_default
        """
        logger.debug("%s set to default", type(self).__name__)
        self._data = self.get_default()

    def set_to_initial_values(self):
        """
        Sets the _data object to be a shallow copy of _initial_data
        :return:
        """
        logger.debug("%s set to initial values", type(self).__name__)
        self._data = self._initial_data.copy()

    @property
    def keys(self) -> list[str]:
        return list(self._data.keys())

    @property
    def values(self) -> list[Any]:
        return list(self._data.values())