from __future__ import annotations
import pandas as pd
from src import PATH_DATASHEET_OUTPUT, JOINT_TYPES_7, SimulationParameters, SimulatorHandler, ExperimentMode, \
    SimulationGapData, ACTION_NAMES

data = [(action_name, None, None) for action_name in ACTION_NAMES]
max_force_list = pd.read_csv(PATH_DATASHEET_OUTPUT)["MaxTorque"].to_list()
test_factors = [0.7,0.8,0.9,1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]
results = {}

sim = SimulatorHandler()
sim.dt = -1
sim.show_ui = False
sim.replays_per_instance = 8
sim.num_instances = 6


for test_factor in test_factors:
    settings = SimulationParameters("maxForceOptimization", "maxVelocity")
    for max_force, motor_index in zip(max_force_list, JOINT_TYPES_7.keys()):
        settings.set_for_joint_type(motor_index, "max_force", max_force * test_factor)
    gap_handler = sim.simulation_gap(settings,data=data, replay_mode= ExperimentMode.DEL_EXISTING)
    results[test_factor] = gap_handler.get_optimization_target()

print(results)
pd.Series(results).to_csv("output_large.csv")