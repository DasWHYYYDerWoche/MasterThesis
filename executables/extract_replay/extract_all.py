from src import SimulatorHandler, ACTION_NAMES, ExperimentMode, get_test_data, get_train_data, get_combined_data
import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',format='%(levelname)s: %(message)s', encoding='utf-8', filemode='w', level=logging.DEBUG)


data = get_combined_data()

sim_handler = SimulatorHandler()
sim_handler.num_instances = 5
sim_handler.show_ui = False

sim_handler.extract(data, mode=ExperimentMode.DEL_EXISTING)