from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class FileHandler(ABC):
    def __init__(self, path: Path):
        self._path = path
        self._data: dict = {}
        self._different_from_file = False
        self._load()

    @abstractmethod
    def _load(self):
        pass

    @abstractmethod
    def get_default(self) -> dict:
        pass

    @abstractmethod
    def _write_to_file(self):
        pass

    def write_to_file(self):
        if not self._different_from_file:
            return
        self._write_to_file()
        self._different_from_file = False

    def set_value(self, key: str, value: Any) -> bool:
        if value is self._data[key]:
            return True
        self._data[key] = value
        self._different_from_file = True
        return True

    def set_values(self, keys: list[str], values: list[Any]):
        if len(keys) != len(values):
            return False
        any_different: bool = False
        for key, value in zip(keys, values):
            if not value is self._data[key]:
                any_different = True
                self._data[key] = value
        if any_different:
            self._different_from_file = True
        return True

    def set_default(self):
        default = self.get_default()
        self.set_values(list(default.keys()), list(default.values()))

    @property
    def keys(self) -> list[str]:
        return list(self._data.keys())

    @property
    def values(self) -> list[Any]:
        return list(self._data.values())