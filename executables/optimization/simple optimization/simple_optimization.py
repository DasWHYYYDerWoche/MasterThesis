from __future__ import annotations
import logging
from datetime import datetime
import logging
import random

import numpy as np
import pandas

from src import SimOptimizer, PARAMETERS_GLOBAL_0, PARAMETERS_PER_TYPE_0, ACTION_NAMES, get_project_root
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s', encoding='utf-8', filemode='w', level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")


results_folder = (get_project_root() / "executables" / "optimization" / "simple optimization")

action_names = ACTION_NAMES
train_indices = [0,1,2,3]
test_indices = [4]
train_data = []
test_data = []
for action_name in action_names:
    train_data.extend([(action_name, "260108", index) for index in train_indices])
    test_data.extend([(action_name, "260108", index) for index in test_indices])

population_size = 30
max_gen = 100
optimizer = SimOptimizer(PARAMETERS_GLOBAL_0, PARAMETERS_PER_TYPE_0,
                         training_data=train_data, test_data=test_data, population_size=population_size,
                         max_gen=max_gen)
optimizer.crossover_pb = 0.5
optimizer.mutation_pb = 0.2
population, logbook, stats, hall_off_fame = optimizer.run()
optimizer.save_last_run(results_folder)