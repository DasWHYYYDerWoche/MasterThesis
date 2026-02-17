from copy import copy

from ..Utils import Hinge, HINGE_NAMES, PATH_REPLAYS
from typing import Optional
from pathlib import Path
from enum import Enum
import json

import logging
logger = logging.getLogger("global_logger")

class SettingsSourceType(Enum):
    NEW = 0
    REPEAT = 1
    NEW_WITH_BASE = 2

class SimulatorSettings:

    def __init__(self, target_param_set_id : str, source_param_set_id : Optional[str] = None):
        self._target_param_set_id : str = target_param_set_id
        self._source_param_set_id : Optional[str] = source_param_set_id

        if self._source_param_set_id:
            if self._target_param_set_id == self._source_param_set_id:
                self._settings_source_type = SettingsSourceType.REPEAT
            else:
                self._settings_source_type = SettingsSourceType.NEW_WITH_BASE
        else:
            self._settings_source_type = SettingsSourceType.NEW
        self._kp : Optional[float] = None
        self._kd : Optional[float] = None
        self._contact_kp : Optional[float] = None
        self._contact_kd : Optional[float] = None
        self._hinge_parameters: dict[str, Hinge] = {}
        if self._settings_source_type is SettingsSourceType.NEW or \
                self._settings_source_type is SettingsSourceType.NEW_WITH_BASE:
            if self.path_settings_target.exists():
                logger.error("The target %s already exists and will be overwritten", self._target_param_set_id)
        if self._settings_source_type is SettingsSourceType.REPEAT or \
            self._settings_source_type is SettingsSourceType.NEW_WITH_BASE:
            if not self.path_settings_source.exists():
                logger.error("The source %s does not exist and cannot be loaded",
                             self._source_param_set_id)
            else:
                self._load_from_file()
        if not self.path_target.exists():
            self.path_target.mkdir(parents=True)

    def save_to_file(self) -> bool:
        if self._settings_source_type is SettingsSourceType.NEW or \
                self._settings_source_type is SettingsSourceType.NEW_WITH_BASE:
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

    def set_hinge_parameter(self, hinge_name, hinge : Hinge) -> bool:
        if self._settings_source_type is SettingsSourceType.NEW or \
                self._settings_source_type is SettingsSourceType.NEW_WITH_BASE:
            if hinge_name in HINGE_NAMES:
                self._hinge_parameters[hinge_name] = hinge
                return True
        return False

    def get_hinge_parameter(self, hinge_name) -> Optional[Hinge]:
        if hinge_name in HINGE_NAMES and hinge_name in self._hinge_parameters.keys():
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
        if self._settings_source_type is SettingsSourceType.NEW or \
                self._settings_source_type is SettingsSourceType.NEW_WITH_BASE:
            self._kp = value

    @kd.setter
    def kd(self, value):
        if self._settings_source_type is SettingsSourceType.NEW or \
                self._settings_source_type is SettingsSourceType.NEW_WITH_BASE:
            self._kd = value

    @contact_kp.setter
    def contact_kp(self, value):
        if self._settings_source_type is SettingsSourceType.NEW or \
                self._settings_source_type is SettingsSourceType.NEW_WITH_BASE:
            self._contact_kp = value

    @contact_kd.setter
    def contact_kd(self, value):
        if self._settings_source_type is SettingsSourceType.NEW or \
                self._settings_source_type is SettingsSourceType.NEW_WITH_BASE:
            self._contact_kd = value

