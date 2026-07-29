from __future__ import annotations
from typing import override
import xml.etree.ElementTree as ElementTree

from ..Constants import PATH_SCENE
from ..Structs import Joint
from .XmlHandler import XmlHandler


class NaoV6H25Handler(XmlHandler):
    """
    File handler for the NaoV6H25.rsi2 file of the simulator. Controls the NAO model and related parameters.
    Since the file is very large the get_default method loads the data from a copy of the file, so make sure you create
    said copy.
    """

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
        super().__init__(PATH_SCENE / "Includes" / "NaoV6H25.rsi2")

    @override
    def _xml_to_dict(self):
        self._data = self._convert(self._xml_tree)

    @staticmethod
    def _convert(xml_tree: ElementTree.ElementTree) -> dict:
        root: ElementTree.Element = xml_tree.getroot()
        data = {}
        for joint_element in root.iter("Hinge"):
            servo_element = joint_element.find("Axis").find("ServoMotor")
            try:
                max_velocity = float(servo_element.get("maxVelocity"))
                max_force = float(servo_element.get("maxForce"))
                p = float(servo_element.get("p"))
                i = float(servo_element.get("i", "0"))
                d = float(servo_element.get("d", "0"))
                hinge = Joint(max_velocity, max_force, p, i, d)
                name = joint_element.get("name")
                data[name[0].lower() + name[1:]] = hinge
            except ValueError:
                raise ValueError
        return data

    @override
    def _dict_to_xml(self):
        root: ElementTree.Element = self._xml_tree.getroot()
        for joint_element in root.iter("Hinge"):
            name = joint_element.get("name")
            hinge = self._data[name[0].lower() + name[1:]]
            servo_element = joint_element.find("Axis").find("ServoMotor")
            servo_element.set("maxVelocity", str(hinge.max_velocity))
            servo_element.set("maxForce", str(hinge.max_force))
            servo_element.set("p", str(hinge.p))
            servo_element.set("i", str(hinge.i))
            servo_element.set("d", str(hinge.d))

    @staticmethod
    @override
    def get_default() -> dict:
        default_tree = ElementTree.parse(PATH_SCENE / "Includes" / "NaoV6H25_BACKUP.rsi2")
        return NaoV6H25Handler._convert(default_tree)

    def set_joint_parameters(self, joint_name: str, joint: Joint):
        self._set_value(joint_name, joint)
