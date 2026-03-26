import json
import logging

from typing import Optional
from pathlib import Path

from ..Utils import Hinge, NAMES, PATH_REPLAYS

logger = logging.getLogger("global_logger")

class SimulationParameters:
    """
    Holds parameters that change the behavior of the simulation like kd/kp values.

    Can be saved to and loaded from a file based on the given ID(s)
    """

    class Type:
        NEW = 0
        REPEAT = 1
        NEW_WITH_BASE = 2

    def __init__(self, target_param_set_id : str, source_param_set_id : Optional[str] = None):
        """
        Creates a new parameter set which saves replays at target_param_set_id.
        If source_param_set_id is given, the settings are loaded from there, otherwise the standard parameters
        are used.

        Setting both target_param_set_id and source_param_set_id to the same value will prevent any changes to
        this object.

        :param target_param_set_id: where replays done with this parameter set are saved
        :param source_param_set_id: from where a parameter set should be loaded
        """
        self._target_param_set_id : str = target_param_set_id
        self._source_param_set_id : Optional[str] = source_param_set_id
        self._kp: Optional[float] = None
        self._kd: Optional[float] = None
        self._contact_kp: Optional[float] = None
        self._contact_kd: Optional[float] = None
        self._hinge_parameters: dict[str, Hinge] = {}
        #setting source parameter
        if self._source_param_set_id:
            if self._target_param_set_id == self._source_param_set_id:
                self._type = SimulationParameters.Type.REPEAT
            else:
                self._type = SimulationParameters.Type.NEW_WITH_BASE
        else:
            self._type = SimulationParameters.Type.NEW
        #check if state is consistent
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            if self.path_settings_target.exists():
                logger.error("The target %s already exists and will be overwritten", self._target_param_set_id)
        if self._type is SimulationParameters.Type.REPEAT or \
            self._type is SimulationParameters.Type.NEW_WITH_BASE:
            if not self.path_settings_source.exists():
                logger.error("The source %s does not exist and cannot be loaded",
                             self._source_param_set_id)
            else:
                self._load_from_file()
        #create folder(s)
        if not self.path_target.exists():
            self.path_target.mkdir(parents=True)
        self.save_to_file()

    def save_to_file(self) -> bool:
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            as_dict = {
                "kp": self._kp,
                "kd": self._kd,
                "contact_kp": self._contact_kp,
                "contact_kd": self._contact_kd,
                "hinge_parameters": {
                    name: hinge.to_dict()
                    for name, hinge in self._hinge_parameters.items()
                },
            }
            with open(self.path_settings_target, "w") as f:
                json.dump(as_dict, f, indent=4)
            return True
        return False

    def _load_from_file(self):
        with open(self.path_settings_source, "r") as f:
            data = json.load(f)
        self._kp = data["kp"]
        self._kd = data["kd"]
        self._contact_kp = data["contact_kp"]
        self._contact_kd = data["contact_kd"]
        self._hinge_parameters = {
            name: Hinge.from_dict(h_data) for name, h_data in data["hinge_parameters"].items()
        }

    def set(self, hinge_name, hinge : Hinge) -> bool:
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            if hinge_name in NAMES:
                self._hinge_parameters[hinge_name] = hinge
                return True
        return False

    def get(self, hinge_name) -> Optional[Hinge]:
        if hinge_name in NAMES and hinge_name in self._hinge_parameters.keys():
            return self._hinge_parameters[hinge_name]
        return None

    @property
    def path_target(self) -> Path:
        return PATH_REPLAYS / ("paramSet_" + self._target_param_set_id)

    @property
    def path_source(self) -> Optional[Path]:
        if self._source_param_set_id:
            return PATH_REPLAYS / ("paramSet_" + self._source_param_set_id)
        return None

    @property
    def path_settings_target(self) -> Path:
        return PATH_REPLAYS / ("paramSet_" + self._target_param_set_id) / "settings.json"

    @property
    def path_settings_source(self) -> Optional[Path]:
        if self._source_param_set_id:
            return PATH_REPLAYS / ("paramSet_" + self._source_param_set_id) / "settings.json"
        return None

    @property
    def target_param_set_id(self):
        return self._target_param_set_id

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
    def hinge_parameters(self):
        return self._hinge_parameters

    @kp.setter
    def kp(self, value):
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            self._kp = value

    @kd.setter
    def kd(self, value):
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            self._kd = value

    @contact_kp.setter
    def contact_kp(self, value):
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            self._contact_kp = value

    @contact_kd.setter
    def contact_kd(self, value):
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            self._contact_kd = value

