from src import SimulatorHandler, SimulationParameters, ACTION_NAMES, ExperimentMode
import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',format='%(levelname)s: %(message)s', encoding='utf-8', filemode='w', level=logging.DEBUG)

data = [(action_name, None, None) for action_name in ACTION_NAMES]

sim_handler = SimulatorHandler()
sim_handler.num_instances = 1
sim_handler.replays_per_instance = 5
sim_handler.show_ui = False
sim_handler.dt = -1

settings = SimulationParameters("defaultFive")
sim_handler.replay(settings, data, mode = ExperimentMode.DEL_EXISTING)