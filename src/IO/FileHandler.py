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
            logger.debug("%s loaded from %s", type(self).__name__, self._path)
        except Exception as e:
            logger.exception("%s failed to load due to %s", type(self).__name__, type(e).__name__)

    def write_to_file(self):
        """
        Write _data object to file.
        """
        try:
            self._write_to_file()
            logger.debug("%s set \"%s\" to \"%s\"", type(self).__name__, self._data.keys(), self._data.values())
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
            return True
        else:
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
            return
        for key,value in zip(keys,values):
            if key in self._data.keys():
                self._data[key] = value

    def get_value(self, key : str) -> Any:
        if key in self._data.keys():
            return self._data[key]
        return None

    def set_default(self):
        """
        Sets the _data object to the dict returned by get_default
        """
        self._data = self.get_default()

    def set_to_initial_values(self):
        """
        Sets the _data object to be a shallow copy of _initial_data
        :return:
        """
        self._data = self._initial_data.copy()

    @property
    def keys(self) -> list[str]:
        return list(self._data.keys())

    @property
    def values(self) -> list[Any]:
        return list(self._data.values())