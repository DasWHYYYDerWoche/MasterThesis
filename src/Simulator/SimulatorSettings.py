from copy import copy

from ..Utils import Hinge, HINGE_NAMES, PATH_REPLAYS
from .ConfigurationHandler import NaoV6H25Handler
from typing import Optional
from pathlib import Path
import json

class SimulatorSettings:

    def __init__(self, param_set_id : str):
        self._param_set_id : str = param_set_id
        self._kp = 0
        self._kd = 0
        self._contact_kp = 0
        self._contact_kd = 0
        self._hinge_parameters: dict[str, Hinge] = {}
        if self.exists():
            self._load_from_file()

    def exists(self) -> bool:
        return self.path_settings.exists()

    def to_dict(self) -> dict:
        return {
            "kp": self._kp,
            "kd": self._kd,
            "contact_kp": self._contact_kp,
            "contact_kd": self._contact_kd,
            "hinge_parameters": {
                name: hinge.to_dict()
                for name, hinge in self._hinge_parameters.items()
            },
        }

    def save_to_file(self):
        with open(self.path_settings, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def _load_from_file(self):
        with open(self.path_settings, "r") as f:
            data = json.load(f)
        self._kp = data["kp"]
        self._kd = data["kd"]
        self._contact_kp = data["contact_kp"]
        self._contact_kd = data["contact_kd"]
        self._hinge_parameters = {
            name: Hinge.from_dict(h_data) for name, h_data in data["hinge_parameters"].items()
        }

    @property
    def path(self) -> Path:
        return PATH_REPLAYS / ("paramSet_" + self._param_set_id)

    @property
    def path_settings(self) -> Path:
        return PATH_REPLAYS / ("paramSet_" + self._param_set_id) / "settings.json"

    def set_hinge_parameters(self, hinge_parameters : dict[str, Hinge]):
        for hinge_name in HINGE_NAMES:
            if hinge_name in hinge_parameters.keys():
                self._hinge_parameters[hinge_name] = hinge_parameters[hinge_name]

    def set_hinge_parameter(self, hinge_name, hinge : Hinge) -> bool:
        if hinge_name in HINGE_NAMES:
            self._hinge_parameters[hinge_name] = hinge
            return True
        return False

    def get_hinge_parameter(self, hinge_name) -> Optional[Hinge]:
        if hinge_name in HINGE_NAMES:
            return self._hinge_parameters[hinge_name]
        return None

    @property
    def kp(self) -> float:
        return self._kp

    @property
    def kd(self) -> float:
        return self._kd

    @property
    def contact_kp(self) -> float:
        return self._contact_kp

    @property
    def contact_kd(self) -> float:
        return self._contact_kd

    @property
    def hinge_parameters(self) -> dict[str, Hinge]:
        return self._hinge_parameters