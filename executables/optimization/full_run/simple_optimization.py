from __future__ import annotations
from src import SimOptimizer, PARAMETERS_GLOBAL_0, PARAMETERS_PER_TYPE_0, ACTION_NAMES, get_project_root, Hyperparameters, SimulatorHandler

from src.Optimizer.Parameter import PARAMETER_SET_0, PARAMETER_SET_1

import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',
                    format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                    encoding='utf-8',
                    filemode='w',
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S")

results_folder = (get_project_root() / "executables" / "optimization" / "full_run")

action_names = ACTION_NAMES
train_indices = [0,1,2,3]
test_indices = [4]
train_data = []
test_data = []
for action_name in action_names:
    train_data.extend([(action_name, "260108", index) for index in train_indices])
    test_data.extend([(action_name, "260108", index) for index in test_indices])

hyperparameters = Hyperparameters(crossover_pb=0.5,
                                  mutation_pb=0.2,
                                  mutation_sigma=10,
                                  mutation_ind_pb=0.2,
                                  tournament_size=3,
                                  init_offset_factor=0.2,
                                  lower_bound_factor=0.1,
                                  upper_bound_factor=10,
                                  pop_size=30,
                                  num_gen=100)

sim_handler = SimulatorHandler()
sim_handler.show_ui = False
sim_handler.num_instances = 3
sim_handler.replays_per_instance = 4
sim_handler.max_wait_for_ready = 2
sim_handler.max_run_duration = 10

optimizer = SimOptimizer(parameters=PARAMETER_SET_1,
                         hyperparameters=hyperparameters,
                         sim_handler=sim_handler,
                         training_data=train_data,
                         test_data=test_data)
optimizer.run()
optimizer.save_last_run(results_folder)