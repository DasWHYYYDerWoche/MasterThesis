from src import SimulatorHandler, ACTION_NAMES, ExperimentMode, get_test_data, get_train_data, get_combined_data
import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',format='%(levelname)s: %(message)s', encoding='utf-8', filemode='w', level=logging.DEBUG)


#data = get_combined_data()

action_names = ["kick_left",
                "walk_front",
                "sidestep_left",
                "turn_left",
                "standup_back", "standup_front"]
train_indices = [0,1,2,3,4]
data = []
for action_name in action_names:
    data.extend([(action_name, "260108", index) for index in train_indices])

sim_handler = SimulatorHandler()
sim_handler.max_run_duration = 20
sim_handler.num_instances = 1
sim_handler.show_ui = False

sim_handler.extract(data, mode=ExperimentMode.DEL_EXISTING)