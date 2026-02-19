from __future__ import annotations
from typing import override
import xml.etree.ElementTree as ElementTree

from ...Utils import XmlHandler, PATH_SCENE

class ThesisCSVReplayHandler(XmlHandler):
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
        super().__init__(PATH_SCENE / "ThesisCSVReplay.ros2")

    @override
    def _xml_to_dict(self):
        element: ElementTree.Element = self._xml_tree.getroot().find("Scene")
        self._data["Kd"] = element.get("Kd")
        self._data["Kp"] = element.get("Kp")
        self._data["contactKp"] = element.get("contactKp")
        self._data["contactKd"] = element.get("contactKd")

    @override
    def _dict_to_xml(self):
        element: ElementTree.Element = self._xml_tree.getroot().find("Scene")
        for key,value in self._data.items():
            element.set(key, str(value))

    @override
    def get_default(self) -> dict:
        return {
            "Kp": 12500,
            "Kd": 10000,
            "contactKp": 1425,
            "contactKd": 7.5
        }

    @property
    def kp(self) -> float:
        return self._data["Kp"]

    @property
    def kd(self) -> float:
        return self._data["Kd"]

    @property
    def contact_kp(self) -> float:
        return self._data["contactKp"]

    @property
    def contact_kd(self) -> float:
        return self._data["contactKd"]

    def set(self, kp: float, kd: float, contact_kp: float, contact_kd: float):
        self._set_values(keys=self.keys, values=[kp, kd, contact_kp, contact_kd])
