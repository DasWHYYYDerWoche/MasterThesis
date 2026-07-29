from __future__ import annotations
from src import SimOptimizer, get_project_root, Hyperparameters, SimulatorHandler, PARAMETER_SET_0, PARAMETER_SET_1, PARAMETER_SET_2
from pathlib import Path
import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',
                    format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                    encoding='utf-8',
                    filemode='w',
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S")

results_folder = (get_project_root() / "executables" / "optimization" / "single_example")

train_data = [("kick_left", "260108", 0)]
test_data = [("kick_left", "260108", 0)]

sim_handler = SimulatorHandler()
sim_handler.show_ui = True
sim_handler.num_instances = 1
sim_handler.replays_per_instance = 12
sim_handler.max_wait_for_ready = 5
sim_handler.max_run_duration = 60
sim_handler.dt = -1
sim_handler._configurationHandler.reset_all()

hyperparameters = Hyperparameters(crossover_pb=0.8,
                                  mutation_pb=0.1,
                                  mutation_ind_pb=0.1,
                                  tournament_size=2,
                                  pop_size=5,
                                  num_gen=11)

optimizer = SimOptimizer(parameters=PARAMETER_SET_2,
                         hyperparameters=hyperparameters,
                         sim_handler=sim_handler,
                         training_data=train_data,
                         test_data=test_data)
#optimizer.run(seed=0,  checkpoint_directory= Path("checkpoint_gen_10.pkl"))
optimizer.load_checkpoint(Path("checkpoint_gen_10.pkl"))
optimizer.save_last_run(results_folder)