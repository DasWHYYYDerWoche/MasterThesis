"""
test script for the optimization which uses a single log for the train and test data.
"""

from __future__ import annotations
from src import SimOptimizer, PROJECT_ROOT, Hyperparameters, SimulatorHandler, PARAMETER_SET_0, PARAMETER_SET_1, PARAMETER_SET_2, PATH_OUTPUT
import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='single_trajectory_optimization.log',
                    format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                    encoding='utf-8',
                    filemode='w',
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S")

results_folder = (PROJECT_ROOT / "executables" / "optimization" / "single_example")

train_data = [("kick_left", "260108", 0)]
test_data = [("kick_left", "260108", 0)]

sim_handler = SimulatorHandler()
sim_handler.show_ui = False
sim_handler.num_instances = 1
sim_handler.replays_per_instance = 1
sim_handler.max_wait_for_ready = 5
sim_handler.max_run_duration = 5
sim_handler.dt = -1

hyperparameters = Hyperparameters(crossover_pb=0.8,
                                  mutation_pb=0.1,
                                  mutation_ind_pb=0.1,
                                  tournament_size=2,
                                  pop_size=5,
                                  num_gen=11)

optimizer = SimOptimizer(parameters=PARAMETER_SET_2, #can be replaced with PARAMETER_SET_0/PARAMETER_SET_1
                         hyperparameters=hyperparameters,
                         sim_handler=sim_handler,
                         training_data=train_data,
                         test_data=test_data)
optimizer.run(seed=0,  checkpoint_directory= PATH_OUTPUT / "single_trajectory_optimization")
#optimizer.load_checkpoint(Path("checkpoint_gen_10.pkl"))
optimizer.save_last_run(PATH_OUTPUT / "single_trajectory_optimization")