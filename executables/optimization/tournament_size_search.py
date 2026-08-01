from __future__ import annotations
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
from src import SimOptimizer,PATH_OUTPUT, Hyperparameters, SimulatorHandler, PARAMETER_SET_2

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

sim_handler = SimulatorHandler()
sim_handler.show_ui = False
sim_handler.num_instances = 2
sim_handler.replays_per_instance = 4
sim_handler.max_wait_for_ready = 5
sim_handler.max_run_duration = 60
sim_handler.dt = -1

for tournament_size in [2,3,4,5,6]:
    hyperparameters = Hyperparameters(crossover_pb=0.8,
                                      mutation_pb=0.1,
                                      mutation_ind_pb=0.1,
                                      tournament_size=tournament_size,
                                      pop_size=30,
                                      num_gen=100)

    optimizer = SimOptimizer(parameters=PARAMETER_SET_2,
                             hyperparameters=hyperparameters,
                             sim_handler=sim_handler,
                             training_data=train_data,
                             test_data=test_data)
    optimizer.run(seed=0, checkpoint_directory= PATH_OUTPUT / "tournament_search")
    optimizer.save_last_run(PATH_OUTPUT / "tournament_search")