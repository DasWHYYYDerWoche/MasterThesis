from typing import Any

from ..Utils import ExperimentParameters, SimulationParameters
from ..IO import LoggerCfgHandler, NaoV6H25Handler, ThesisCSVReplayHandler, ThesisLogExtractionHandler

class ConfigurationHandler:
    """
    Used by the Simulator to handle all configuration files needed for log extraction and replaying.

    This is a singleton to ensure files are always only written to from one source.
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
        self._loggerCfgHandler = LoggerCfgHandler()
        self._naoV6H25Handler = NaoV6H25Handler()
        self._thesisCSVReplayHandler = ThesisCSVReplayHandler()
        self._thesisLogExtractionHandler = ThesisLogExtractionHandler()

    def set_extraction_parameters(self, parameters : ExperimentParameters):
        self._loggerCfgHandler.set_extract(parameters.extraction_path_relative.as_posix(), parameters.recording_duration)
        self._loggerCfgHandler.write_to_file()
        self._thesisLogExtractionHandler.set(parameters.log_path_relative.as_posix())
        self._thesisLogExtractionHandler.write_to_file()

    def set_replay_parameters(self, eps : list[ExperimentParameters]):
        self._loggerCfgHandler.set_default()
        for ep in eps:
            self._loggerCfgHandler.append_replay(ep.extraction_path_relative.as_posix(),
                                                 ep.replay_path_relative.as_posix(),
                                                 ep.move_robot)
        self._loggerCfgHandler.write_to_file()
        self._thesisLogExtractionHandler.set_default()
        self._thesisLogExtractionHandler.write_to_file()

    def set_simulation_parameters(self, parameters : SimulationParameters):
        if parameters.Kd:
            self._thesisCSVReplayHandler.kd = parameters.Kd
        if parameters.Kp:
            self._thesisCSVReplayHandler.kp = parameters.Kp
        if parameters.contactKd:
            self._thesisCSVReplayHandler.contact_kd = parameters.contactKd
        if parameters.contactKp:
            self._thesisCSVReplayHandler.contact_kp = parameters.contactKp
        self._thesisCSVReplayHandler.write_to_file()
        for hinge_name, hinge in parameters.joint_parameters.items():
            self._naoV6H25Handler.set_joint_parameters(hinge_name, hinge)
        self._naoV6H25Handler.write_to_file()

    def reset_experiment_parameters(self):
        self._loggerCfgHandler.set_default()
        self._loggerCfgHandler.write_to_file()
        self._thesisLogExtractionHandler.set_default()
        self._thesisLogExtractionHandler.write_to_file()

    def reset_simulation_parameters(self):
        self._thesisCSVReplayHandler.set_default()
        self._thesisCSVReplayHandler.write_to_file()
        self._naoV6H25Handler.set_default()
        self._naoV6H25Handler.write_to_file()

    def reset_all(self):
        self.reset_experiment_parameters()
        self.reset_simulation_parameters()

    def get_parameter_value(self, parameter_name) -> Any:
        val = self._loggerCfgHandler.get_value(parameter_name)
        if val is not None:
            return val
        val = self._naoV6H25Handler.get_value(parameter_name)
        if val is not None:
            return val
        val = self._thesisCSVReplayHandler.get_value(parameter_name)
        if val is not None:
            return val
        val = self._thesisLogExtractionHandler.get_value(parameter_name)
        return val

    def get_default_value(self, parameter_name):
        d = self._loggerCfgHandler.get_default()
        if parameter_name in d.keys():
            return d[parameter_name]
        d = self._naoV6H25Handler.get_default()
        if parameter_name in d.keys():
            return d[parameter_name]
        d = self._thesisCSVReplayHandler.get_default()
        if parameter_name in d.keys():
            return d[parameter_name]
        d = self._thesisLogExtractionHandler.get_default()
        if parameter_name in d.keys():
            return d[parameter_name]
        return None