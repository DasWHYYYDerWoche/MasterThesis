from __future__ import annotations
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


from src import SimOptimizer,get_project_root, Hyperparameters, SimulatorHandler

from src.Optimizer.Parameter import PARAMETER_SET_0, PARAMETER_SET_1, PARAMETER_SET_2
from src import get_test_data, get_train_data, get_combined_data

import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',
                    format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                    encoding='utf-8',
                    filemode='w',
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S")

results_folder = (get_project_root() / "executables" / "optimization" / "full_run")

train_data = get_train_data()
test_data = get_test_data()
"""
action_names = ["kick_left",
                "walk_front",
                "sidestep_left",
                "turn_left",
                "standup_back", "standup_front"]
train_indices = [0,1,2,3]
test_indices = [4]
train_data = []
test_data = []
for action_name in action_names:
    train_data.extend([(action_name, "260108", index) for index in train_indices])
    test_data.extend([(action_name, "260108", index) for index in test_indices])
"""

sim_handler = SimulatorHandler()
sim_handler.show_ui = False
sim_handler.num_instances = 1
sim_handler.replays_per_instance = 12
sim_handler.max_wait_for_ready = 5
sim_handler.max_run_duration = 60
sim_handler.dt = -1

hyperparameters = Hyperparameters(crossover_pb=0.8,
                                  mutation_pb=0.1,
                                  mutation_ind_pb=0.1,
                                  tournament_size=2,
                                  pop_size=30,
                                  num_gen=100)

optimizer = SimOptimizer(parameters=PARAMETER_SET_2,
                         hyperparameters=hyperparameters,
                         sim_handler=sim_handler,
                         training_data=train_data,
                         test_data=test_data)
optimizer.run(seed=0)
optimizer.save_last_run(results_folder)