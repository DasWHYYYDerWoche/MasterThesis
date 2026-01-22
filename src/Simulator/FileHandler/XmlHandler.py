from __future__ import annotations
from abc import ABC, abstractmethod
from typing import override
import xml.etree.ElementTree as ET
from pathlib import Path

from .FileHandler import FileHandler
from ..Utils import Hinge


class XmlHandler(FileHandler):
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
    def __init__(self, path_scene: Path):
        super().__init__(path_scene / "ThesisCSVReplay.ros2")

    @override
    def _xml_to_dict(self):
        element: ET.Element = self._xml_tree.getroot().find("Scene")
        self._data["Kd"] = element.get("Kd")
        self._data["Kp"] = element.get("Kp")
        self._data["contactKp"] = element.get("contactKp")
        self._data["contactKd"] = element.get("contactKd")

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
        self.set_values(keys=self.keys, values=[kp,kd,contact_kp,contact_kd])



class NaoV6H25Handler(XmlHandler):
    def __init__(self, path_config: Path):
        super().__init__(path_config / "Includes" / "NaoV6H25.rsi2")

    def _xml_to_dict(self):
        root: ET.Element = self._xml_tree.getroot()

        for hinge_element in root.iter("Hinge"):
            servo_element = hinge_element.find("Axis").find("ServoMotor")
            try:
                max_velocity = float(servo_element.get("maxVelocity"))
                max_force = float(servo_element.get("maxForce"))
                p = float(servo_element.get("p"))
                i = float(servo_element.get("i", "0"))
                d = float(servo_element.get("d", "0"))
                hinge = Hinge(max_velocity, max_force, p, i, d)
                self._data[hinge_element.get("name")] = hinge
            except ValueError:
                raise ValueError

    def _dict_to_xml(self):
        root: ET.Element = self._xml_tree.getroot()
        for hinge_element in root.iter("Hinge"):

            pass

    def get_default(self) -> dict:
        pass