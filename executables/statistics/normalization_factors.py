"""
calculates the normalization factors for the simulation gap calculation and saves them to the output2.csv file.

This file is loaded by the SimulationGapHandler class and needs to be created before running the optimization.
"""
from src import (DEFLECTIONS, PATH_DATASHEET_OUTPUT, JOINT_NAMES, PATH_OUTPUT,
                 get_combined_data, ExperimentParameters, get_extraction_path_full)
import numpy as np
import pandas as pd

#position factor
max_pos = []
for key in DEFLECTIONS.keys():
    if key != "lHand" and key != "rHand" and key != "headYaw" and key != "headPitch":
        lower, upper = DEFLECTIONS[key]
        max_pos.append(max(abs(lower), abs(upper)))
max_max_pos = np.average(max_pos)

#velocity factor
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

#acceleration factor
data = get_combined_data()
eps = ExperimentParameters.create_experiment_parameters(None,data)
accelerations = {joint : [] for joint in JOINT_NAMES}
for ep in eps:
    extraction_path = get_extraction_path_full(ep.action_name, ep.recording_date, ep.log_index)
    df = pd.read_csv(extraction_path.with_suffix(".csv"), sep=";")
    dt = np.diff((df['time_step'] - df['time_step'][0])  / 1000 )
    for joint_name in JOINT_NAMES:
        pos = df["sensor_" + joint_name]
        vel = list(np.diff(pos) / dt[0:])
        acc = list(np.diff(vel) / dt[1:])
        acc_greater_zero = [val for val in np.abs(acc) if val > 0]
        accelerations[joint_name].extend(acc_greater_zero)

max_acc = []
for joint_acceleration in accelerations.values():
    max_acc.append(np.nanmax(joint_acceleration))

max_max_acc = np.nanmean(max_acc)
df = pd.DataFrame.from_dict({"pos" : [max_max_pos], "vel" : [max_max_vel], "acc" : [max_max_acc]})
df.to_csv(PATH_OUTPUT / "normalization_factors.csv")