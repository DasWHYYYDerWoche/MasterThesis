from __future__ import annotations
from src import SimOptimizer, get_project_root, Hyperparameters, SimulatorHandler, PARAMETER_SET_0, PARAMETER_SET_1

import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',
                    format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                    encoding='utf-8',
                    filemode='w',
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S")

results_folder = (get_project_root() / "executables" / "optimization" / "single_example")

train_data = [("kick", "260108", 0)]
test_data = [("kick", "260108", 0)]

hyperparameters = Hyperparameters(crossover_pb=0.5,
                                  mutation_pb=0.2,
                                  mutation_sigma=10,
                                  mutation_ind_pb=0.2,
                                  tournament_size=3,
                                  init_offset_factor=0.2,
                                  lower_bound_factor=0.1,
                                  upper_bound_factor=10,
                                  pop_size=10,
                                  num_gen=20)

sim_handler = SimulatorHandler()
sim_handler.show_ui = False
sim_handler.num_instances = 1
sim_handler.replays_per_instance = 1
sim_handler.max_wait_for_ready = 2
sim_handler.max_run_duration = 5

optimizer = SimOptimizer(PARAMETER_SET_0,
                         hyperparameters=hyperparameters,
                         sim_handler=sim_handler,
                         training_data=train_data,
                         test_data=test_data)
optimizer.run()
optimizer.save_last_run(results_folder)