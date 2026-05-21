import numpy as np
import pandas as pd
import math

from src import DEFLECTIONS, PATH_DATASHEET_OUTPUT, ACTION_NAMES, SimulationGapHandler, SimulatorHandler, \
    SimulationParameters, JOINT_NAMES

deflections = []
for key in DEFLECTIONS.keys():
    if key != "lHand" and key != "rHand":
        lower, upper = DEFLECTIONS[key]
        deflections.append(max(abs(lower), abs(upper)))
print("pos_norm: " + str(np.average(deflections)))


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
print("vel_norm (no hands): " + str(np.average(max_velocities, weights=weights)))


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
means = []
percentiles_25 = []
percentiles_75 = []
max_non_outlier = []
for joint_acceleration in accelerations.values():
    percentiles.append(np.nanpercentile(joint_acceleration, 99.5))
    mean = np.nanmean(joint_acceleration)
    percentile_25 = np.nanpercentile(joint_acceleration, 25)
    percentiles_25.append(percentile_25)
    percentile_75 = np.nanpercentile(joint_acceleration, 75)
    percentiles_75.append(percentile_75)
    itqd = percentile_75 - percentile_25

    means.append(mean)
    max_non_outlier.append(percentile_75 + 1.5*itqd)

print(percentiles_25)
print(percentiles_75)

print("acc_norm (percentile): " + str(np.average(percentiles)))
print("acc_norm (average): " + str(np.average(max_non_outlier)))