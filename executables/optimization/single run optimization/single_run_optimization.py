from __future__ import annotations
from src import SimOptimizer, PARAMETERS_GLOBAL_0, PARAMETERS_PER_TYPE_0, get_project_root, Hyperparameters, SimulatorHandler

import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',
                    format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                    encoding='utf-8',
                    filemode='w',
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S")

results_folder = (get_project_root() / "executables" / "optimization" / "single run optimization")

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

optimizer = SimOptimizer(global_attributes=PARAMETERS_GLOBAL_0,
                         per_joint_type_attributes=PARAMETERS_PER_TYPE_0,
                         hyperparameters=hyperparameters,
                         sim_handler=sim_handler,
                         training_data=train_data,
                         test_data=test_data)
optimizer.run()
optimizer.save_last_run(results_folder)