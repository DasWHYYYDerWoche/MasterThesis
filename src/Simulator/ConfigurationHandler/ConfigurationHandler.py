from .LoggerCfgHandler import LoggerCfgHandler
from .NaoV6H25Handler import NaoV6H25Handler
from .ThesisCSVReplayHandler import ThesisCSVReplayHandler
from .ThesisLogExtractionHandler import ThesisLogExtractionHandler

from ...Utils import ExperimentParameters, ExperimentType, SimulationParameters

class ConfigurationHandler:
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

    def set_experiment_parameters(self, parameters : ExperimentParameters) -> bool:
        if parameters.experiment_type is ExperimentType.LOG_EXTRACTION:
            self._loggerCfgHandler.set_extract(parameters.extraction_path_relative.as_posix())
            self._loggerCfgHandler.write_to_file()
            self._thesisLogExtractionHandler.set(parameters.log_path.as_posix())
            self._thesisLogExtractionHandler.write_to_file()
            return True
        elif parameters.experiment_type is ExperimentType.CSV_REPLAY:
            self._loggerCfgHandler.set_replay(parameters.extraction_path_relative.as_posix(),
                                              parameters.replay_path_relative.as_posix())
            self._loggerCfgHandler.write_to_file()
            self._thesisLogExtractionHandler.set_default()
            self._thesisLogExtractionHandler.write_to_file()
            return True
        else:
            return False

    def set_simulation_parameters(self, parameters : SimulationParameters):
        self._thesisCSVReplayHandler.set(parameters.kd, parameters.kp, parameters.contact_kd, parameters.contact_kp)
        self._thesisCSVReplayHandler.write_to_file()
        for hinge_name, hinge in parameters.hinge_parameters.items():
            self._naoV6H25Handler.set_hinge_parameters(hinge_name, hinge)
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

