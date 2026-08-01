"""
Runs the optimizer with the parameters from the thesis. Note that a full run will take up to 10 days depending on the hardware.
For systems system with modern hardware the num_instances parameter can be increased to 4 to 12.
"""

from __future__ import annotations
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from src import SimOptimizer,PATH_OUTPUT, Hyperparameters, SimulatorHandler, PARAMETER_SET_2, get_test_data, get_train_data

import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',
                    format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                    encoding='utf-8',
                    filemode='w',
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S")

train_data = get_train_data()
test_data = get_test_data()

sim_handler = SimulatorHandler()
sim_handler.show_ui = False
sim_handler.num_instances = 2
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
optimizer.run(seed=0, checkpoint_directory= PATH_OUTPUT / "full_optimization")
optimizer.save_last_run(PATH_OUTPUT / "full_optimization")