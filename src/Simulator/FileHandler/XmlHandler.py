from __future__ import annotations
from abc import ABC, abstractmethod
from typing import override
import xml.etree.ElementTree as ET
from pathlib import Path

from .FileHandler import FileHandler
from ..Simulator import PATH_SCENE


class XmlHandler(ABC, FileHandler):
    def __init__(self, path: Path):
        self._xml_tree: ET.ElementTree = ET.ElementTree()
        super().__init__(path)

    def _load(self):
        self._xml_tree = ET.parse(self._path)
        self._xml_to_dict()

    def _write_to_file(self):
        self._dict_to_xml()
        self._xml_tree.write(self._path)

    @abstractmethod
    def _xml_to_dict(self):
        pass

    @abstractmethod
    def _dict_to_xml(self):
        pass



class ThesisCSVReplayHandler(XmlHandler):
    def __init__(self):
        super().__init__(PATH_SCENE / "ThesisCSVReplay.ros2")

    @override
    def _xml_to_dict(self):
        element: ET.Element = self._xml_tree.getroot().find("Scene")
        self._data["Kd"] = element.get(key="Kd")
        self._data["Kp"] = element.get(key="Kp")
        self._data["contactKp"] = element.get(key="contactKp")
        self._data["contactKd"] = element.get(key="contactKd")

    @override
    def _dict_to_xml(self):
        element: ET.Element = self._xml_tree.getroot().find("Scene")
        for key,value in self._data:
            element.set(key, str(value))

    @override
    def get_default(self) -> dict:
        return {
            "Kp": 12500,
            "Kd": 10000,
            "contactKp": 1425,
            "contactKd": 7.5
        }

    def set(self, kp: float, kd: float, contact_kp: float, contact_kd: float):
        self.set_values(keys=self._keys, values=[kp,kd,contact_kp,contact_kd])



class NaoV6H25Handler(XmlHandler):
    def __init__(self):
        super().__init__(PATH_SCENE / "Includes" / "NaoV6H25.rsi2")

    def _xml_to_dict(self):
        pass

    def _dict_to_xml(self):
        pass

    def get_default(self) -> dict:
        pass