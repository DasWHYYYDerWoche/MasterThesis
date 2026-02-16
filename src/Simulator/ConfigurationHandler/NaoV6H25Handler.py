from __future__ import annotations
from typing import override
import xml.etree.ElementTree as ElementTree

from ...Utils import XmlHandler, Hinge, PATH_SCENE

class NaoV6H25Handler(XmlHandler):

    def __init__(self):
        super().__init__(PATH_SCENE / "Includes" / "NaoV6H25.rsi2")

    @override
    def _xml_to_dict(self):
        self._data = self._convert(self._xml_tree)

    @staticmethod
    def _convert(xml_tree : ElementTree.ElementTree) -> dict:
        root: ElementTree.Element = xml_tree.getroot()
        data = {}
        for hinge_element in root.iter("Hinge"):
            servo_element = hinge_element.find("Axis").find("ServoMotor")
            try:
                max_velocity = float(servo_element.get("maxVelocity"))
                max_force = float(servo_element.get("maxForce"))
                p = float(servo_element.get("p"))
                i = float(servo_element.get("i", "0"))
                d = float(servo_element.get("d", "0"))
                hinge = Hinge(max_velocity, max_force, p, i, d)
                data[hinge_element.get("name")] = hinge
            except ValueError:
                raise ValueError
        return data

    @override
    def _dict_to_xml(self):
        root: ElementTree.Element = self._xml_tree.getroot()
        for hinge_element in root.iter("Hinge"):
            hinge = self._data[hinge_element.get("name")]
            servo_element = hinge_element.find("Axis").find("ServoMotor")
            servo_element.set("maxVelocity", str(hinge.max_velocity))
            servo_element.set("maxForce", str(hinge.max_force))
            servo_element.set("p", str(hinge.p))
            servo_element.set("i", str(hinge.i))
            servo_element.set("d", str(hinge.d))
            pass

    @staticmethod
    @override
    def get_default() -> dict:
        default_tree = ElementTree.parse(PATH_SCENE / "Includes" / "NaoV6H25_BACKUP.rsi2")
        return NaoV6H25Handler._convert(default_tree)