import numpy as np
import pandas as pd
import math

from src import DEFLECTIONS, PATH_DATASHEET_OUTPUT, ACTION_NAMES, SimulationGapHandler, SimulatorHandler, \
    SimulationParameters, JOINT_NAMES

max_pos = []
for key in DEFLECTIONS.keys():
    if key != "lHand" and key != "rHand":
        lower, upper = DEFLECTIONS[key]
        max_pos.append(max(abs(lower), abs(upper)))
max_max_pos = np.average(max_pos)

max_velocities = pd.read_csv(PATH_DATASHEET_OUTPUT)["MaxSpeed_deg_per_s"].to_list()
joint_types = {
    0 : ["lHipYawPitch", "rHipYawPitch", "lHipRoll", "rHipRoll", "lAnkleRoll", "rAnkleRoll"],
    1 : ["lWristYaw", "rWristYaw"],
    1.5 : [],
    2 : ["headYaw", "lElbowYaw", "rElbowYaw"],
    2.5 : ["headPitch", "lShoulderRoll", "rShoulderRoll", "lElbowRoll", "rElbowRoll"],
    3 : ["lShoulderPitch", "rShoulderPitch"],
    4 : ["lHipPitch", "rHipPitch", "lKneePitch", "rKneePitch", "lAnklePitch", "rAnklePitch"]
}
weights = [len(value) for value in joint_types.values()]
max_max_vel = np.average(max_velocities, weights=weights)


data = [(action_name, None, None) for action_name in ACTION_NAMES]
simulator = SimulatorHandler()
replay_settings = SimulationParameters("default")
gap_handler = simulator.simulation_gap(settings=replay_settings, data=data)
gap_datas = gap_handler._sim_gap_data
accelerations = {joint : [] for joint in JOINT_NAMES}
for gap_datas_for_action in gap_datas.values():
    for gap_data in gap_datas_for_action:
        for joint, acceleration in gap_data.get_acc_extraction(JOINT_NAMES).items():
            accelerations[joint].extend([val for val in np.abs(acceleration) if val > 0])
percentiles = []
for joint_acceleration in accelerations.values():
    percentile = np.nanpercentile(joint_acceleration, 99.9)
    percentiles.append(percentile)
    print(percentile)

max_max_acc = np.nanmean(percentiles)
df = pd.DataFrame.from_dict({"pos" : [max_max_pos], "vel" : [max_max_vel], "acc" : [max_max_acc]})
df.to_csv("output2.csv")