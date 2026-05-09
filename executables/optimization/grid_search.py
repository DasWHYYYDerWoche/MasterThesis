from __future__ import annotations

from datetime import datetime
import logging
import random

import numpy as np
import pandas

from src import SimOptimizer, PARAMETERS_GLOBAL_0, PARAMETERS_PER_TYPE_0, ACTION_NAMES, get_project_root

logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s', encoding='utf-8', filemode='w', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

""" crossover:
for i in range(0, len(indices)):
    test_indices = {action_name : train_test_split[action_name][i] for action_name in ACTION_NAMES}
    train_indices = {action_name : [x for x in train_test_split[action_name] if x != test_indices[action_name]] for action_name in ACTION_NAMES}
    test_data = [(action_name, "260108", index) for action_name, index in test_indices.items()]
    train_data = []
    for action_name in ACTION_NAMES:
        for index in train_indices[action_name]:
            train_data.append((action_name, "260108", index))
    print(test_data)
    print(train_data)
    print()
"""
start_time = datetime.now()
indices: list[int] = [0,1,2,3,4]
crossover_pbs: list[float] = [0.2, 0.4, 0.6, 0.8]
mutation_pbs: list[float] = [0.1, 0.15, 0.2, 0.25, 0.3]
train_test_split = {action_name: list(np.random.permutation(indices)) for action_name in ACTION_NAMES}
test_indices: dict[str, int] = {}
train_indices: dict[str, list[int]] = {}
for action_name in ACTION_NAMES:
    test = random.choice(indices)
    train = [i for i in indices if i != test]
    test_indices[action_name] = test
    train_indices[action_name] = train
test_data = [(action_name, "260108", index) for action_name, index in test_indices.items()]
train_data_lists = [[(action_name, "260108", index) for index in indices] for action_name, indices in
                    train_indices.items()]
train_data = []
for l in train_data_lists:
    for o in l:
        train_data.append(o)

population_size = 20
max_gen = 30
results_folder = (get_project_root() / "executables" / "optimization" / "grid_search_results") / datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
optimizer = SimOptimizer(PARAMETERS_GLOBAL_0, PARAMETERS_PER_TYPE_0,
                         training_data=train_data, test_data=test_data, population_size=population_size,
                         max_gen=max_gen)
for crossover_pb in crossover_pbs:
    for mutation_pb in mutation_pbs:
        optimizer.crossover_pb = crossover_pb
        optimizer.mutation_pb = mutation_pb
        population, logbook, stats, hall_off_fame = optimizer.run()
        optimizer.save_last_run(results_folder)
smallest_test_result = 10000
individual = []
opt_mutation_pb = 0
opt_crossover_pb = 0
for result in results_folder.iterdir():
    df = pandas.read_csv(result / "hallOfFame")
    min_row = df.loc[df["test results"].idxmin()]
    if min_row["test results"] < smallest_test_result:
        smallest_test_result = min_row["test results"]
        individual = list(min_row.drop("test results"))
        hyperparameters = {}
        with open(result / "Hyperparameters.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line:
                    key, value = line.split("=")
                    hyperparameters[key.strip()] = float(value.strip())
        opt_mutation_pb = hyperparameters["crossover_pb"]
        opt_crossover_pb = hyperparameters["mutation_pb"]
duration = datetime.now() - start_time
text = ""
text += "population_size =" + str(population_size) + "\n"
text += "opt_mutation_pb =" + str(opt_mutation_pb) + "\n"
text += "opt_crossover_pb =" + str(opt_crossover_pb) + "\n"
text += "generations =" + str(max_gen) + "\n"
text += "smallest_test_result =" + str(smallest_test_result) + "\n"
text += "best_individual =" + str(individual) + "\n"
text += "duration =" + str(duration) + "\n"
f = None
try:
    f = open(results_folder / "Log.txt", "w")
    f.write(text)
except Exception as e:
    raise e
finally:
    if f is not None:
        f.close()









