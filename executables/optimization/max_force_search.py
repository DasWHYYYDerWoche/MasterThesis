"""
performs the linear search over the different gearbox efficiencies for the max force parameter.
For systems system with modern hardware the num_instances parameter can be increased to 4 to 12.

Note that this script assumes the max_force was previously calculated using the related script in the statistics folder.
"""

from __future__ import annotations
import pandas as pd
from src import (PATH_OUTPUT, PATH_DATASHEET_OUTPUT, JOINT_TYPES_7,
                 SimulationParameters, SimulatorHandler, ExperimentMode, get_combined_data)
import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='max_force_search.log',
                    format='%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                    encoding='utf-8',
                    filemode='w',
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S")



data = get_combined_data()
max_force_list = pd.read_csv(PATH_DATASHEET_OUTPUT)["MaxTorque"].to_list()
test_factors = [0.7,0.8,0.9,
                1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,
                2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9]

results = {}

sim = SimulatorHandler()
sim.dt = -1
sim.show_ui = False
sim.replays_per_instance = 12
sim.max_run_duration = 60
sim.max_wait_for_ready = 5
sim.num_instances = 4 # 2 for 100% cpu usage on uni pc. Can be increased if your computer is better than a toaster.


for test_factor in test_factors:
    settings = SimulationParameters("max_force_" + str(test_factor) + "_home")
    settings.load_max_velocity() # use updated max_velocity values
    for max_force, motor_index in zip(max_force_list, JOINT_TYPES_7.keys()):
        settings.set_for_joint_type(motor_index, "max_force", max_force * test_factor)
        settings.save_to_file()
    gap_handler = sim.simulation_gap(settings,data=data, replay_mode=ExperimentMode.PARTIAL)
    results[test_factor] = gap_handler.get_optimization_target()

pd.Series(results).to_csv(PATH_OUTPUT / "max_force_search.csv")