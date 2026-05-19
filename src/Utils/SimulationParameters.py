import json
import logging

from typing import Optional, Any
from pathlib import Path
import pandas as pd

from .. import ThesisCSVReplayRosHandler
from ..IO import NaoV6H25Handler
from ..Constants import JOINT_NAMES, PATH_REPLAYS, JOINT_TYPES_7, PATH_OUTPUT_MAX_FORCE, PATH_OUTPUT_MAX_VELOCITY
from ..Structs import Joint

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
        defaults = ThesisCSVReplayRosHandler.get_default()
        self._Kd = defaults["Kd"]
        self._Kp = defaults["Kp"]
        self._contactKd = defaults["contactKd"]
        self._contactKp  = defaults["contactKp"]
        self._joint_parameters: dict[str, Joint] = NaoV6H25Handler.get_default()
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
                logger.warning("The target %s already exists and will be overwritten", self._target_param_set_id)
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

    def save_to_file(self) -> bool:
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            as_dict = {
                "Kp": self._Kp,
                "Kd": self._Kd,
                "contactKp": self._contactKp,
                "contactKd": self._contactKd,
                "hinge_parameters": {
                    name: hinge.to_dict() for name, hinge in self._joint_parameters.items()
                },
            }
            with open(self.path_settings_target, "w") as f:
                json.dump(as_dict, f, indent=4)
            return True
        return False

    def _load_from_file(self):
        with open(self.path_settings_source, "r") as f:
            data = json.load(f)
        self._Kp = data["Kp"]
        self._Kd = data["Kd"]
        self._contactKp = data["contactKp"]
        self._contactKd = data["contactKd"]
        self._joint_parameters = {
            name: Joint.from_dict(h_data) for name, h_data in data["hinge_parameters"].items()
        }

    def load_max_force(self):
        data = pd.read_csv(PATH_OUTPUT_MAX_FORCE)
        max_force_list = data["MaxTorque"].to_list()
        for max_force, joint_list in zip(max_force_list, JOINT_TYPES_7.values()):
            for joint in [self._joint_parameters[joint_name] for joint_name in joint_list]:
                joint.max_force = max_force

    def load_max_velocity(self):
        data = pd.read_csv(PATH_OUTPUT_MAX_FORCE)
        max_velocity_list = data["MaxSpeed_rad_per_s"].to_list()
        print(max_velocity_list)
        for max_velocity, joint_list in zip(max_velocity_list, JOINT_TYPES_7.values()):
            for joint in [self._joint_parameters[joint_name] for joint_name in joint_list]:
                joint.max_velocity = max_velocity

    def set(self,
            joint_name : str,
            max_velocity : Optional[float] = None,
            max_force : Optional[float] = None,
            p : Optional[float] = None,
            i : Optional[float] = None,
            d : Optional[float] = None):
        joint = self._joint_parameters[joint_name]
        if max_velocity is not None:
            joint.max_velocity = max_velocity
        if max_force is not None:
            joint.max_velocity = max_force
        if p is not None:
            joint.max_velocity = p
        if i is not None:
            joint.max_velocity = i
        if d is not None:
            joint.max_velocity = d

    def get(self, joint_name) -> Optional[Joint]:
        if joint_name in JOINT_NAMES and joint_name in self._joint_parameters.keys():
            return self._joint_parameters[joint_name]
        return None

    def set_for_joint_type(self, joint_type : float, parameter_name : str, value : Any):
        for joint in [self._joint_parameters[joint_name] for joint_name in JOINT_TYPES_7[joint_type]]:
            setattr(joint, parameter_name, value)

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
    def Kp(self) -> float:
        return self._Kp

    @property
    def Kd(self) -> float:
        return self._Kd

    @property
    def contactKp(self) -> float:
        return self._contactKp

    @property
    def contactKd(self) -> float:
        return self._contactKd

    @property
    def joint_parameters(self):
        return self._joint_parameters

    @Kp.setter
    def Kp(self, value):
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            self._Kp = value

    @Kd.setter
    def Kd(self, value):
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            self._Kd = value

    @contactKp.setter
    def contactKp(self, value):
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            self._contactKp = value

    @contactKd.setter
    def contactKd(self, value):
        if self._type is SimulationParameters.Type.NEW or \
                self._type is SimulationParameters.Type.NEW_WITH_BASE:
            self._contactKd = value


def sim_params_from_file(path : Path, index : int) -> Optional[SimulationParameters]:
    df = pd.read_csv(path)
    if index < 0 or index >= len(df):
        return None
    as_dict = df.iloc[index].to_dict()
    sim_params = SimulationParameters(path.parent.name)
    if "Kp" in as_dict.keys():
        sim_params.Kp = as_dict["Kp"]
    if "Kd" in as_dict.keys():
        sim_params.Kd = as_dict["Kd"]
    if "contactKd" in as_dict.keys():
        sim_params.contactKd = as_dict["contactKd"]
    if "contactKp" in as_dict.keys():
        sim_params.contactKp = as_dict["contactKp"]
    for i in range(len(JOINT_TYPES_7.keys())):
        if "p" + str(i) in as_dict.keys():
            sim_params.set_for_joint_type(i, "p", as_dict["p" + str(i)])
        if "d" + str(i) in as_dict.keys():
            sim_params.set_for_joint_type(i, "d", as_dict["d" + str(i)])
    return sim_params