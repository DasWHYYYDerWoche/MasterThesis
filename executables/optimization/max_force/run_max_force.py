from __future__ import annotations
import pandas as pd
from src import PATH_DATASHEET_OUTPUT, JOINT_TYPES_7, SimulationParameters, SimulatorHandler, ExperimentMode, \
    SimulationGapData, ACTION_NAMES, get_combined_data

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
sim.max_run_duration = 45
sim.max_wait_for_ready = 5
sim.num_instances = 2


for test_factor in test_factors:
    settings = SimulationParameters("max_force_" + str(test_factor))
    settings.load_max_velocity()
    for max_force, motor_index in zip(max_force_list, JOINT_TYPES_7.keys()):
        settings.set_for_joint_type(motor_index, "max_force", max_force * test_factor)
        settings.save_to_file()
    gap_handler = sim.simulation_gap(settings,data=data, replay_mode=ExperimentMode.PARTIAL)
    results[test_factor] = gap_handler.get_optimization_target()

pd.Series(results).to_csv("output.csv")