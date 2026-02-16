from copy import copy

from ..Utils import Hinge, HINGE_NAMES, PATH_REPLAYS
from .FileHandler import NaoV6H25Handler
from typing import Optional
from pathlib import Path

class SimulatorData:

    def __int__(self, param_set_id : str):
        self._param_set_id : str = param_set_id
        self._kp = 0
        self._kd = 0
        self._contact_kp = 0
        self._contact_kd = 0
        self._hinge_parameters: dict[str, Hinge] = {}
        if self.exists():
            pass
        else:
            pass

    def exists(self) -> bool:
        return self.path_settings.exists()

    def _load_from_file(self):
        pass

    def _load_default(self):
        self._hinge_parameters = copy(NaoV6H25Handler.get_default())


    @property
    def path(self) -> Path:
        return PATH_REPLAYS / ("paramSet_" + self._param_set_id)

    @property
    def path_settings(self) -> Path:
        return PATH_REPLAYS / ("paramSet_" + self._param_set_id) / "settings.txt"


    def __init__(self, kp : float = 12500, kd = 10000, contact_kp = 1425, contact_kd = 7.5, hinge_parameters : dict[str, Hinge] | None = None):
        self._kp = kp
        self._kd = kd
        self._contact_kp = contact_kp
        self._contact_kd = contact_kd
        self._hinge_parameters : dict[str, Hinge] = hinge_parameters or {}
        self.set_hinge_parameters(hinge_parameters)

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