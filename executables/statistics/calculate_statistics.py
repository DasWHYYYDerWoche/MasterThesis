from __future__ import annotations

from src import SimulatorHandler, ExperimentParameters, get_extraction_path_full, JOINT_NAMES
import pandas
import numpy as np

import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',format='%(levelname)s: %(message)s', encoding='utf-8', filemode='w', level=logging.DEBUG)

def f_min(row):
    row.iloc[1:].min()

def f_max(row):
    row.iloc[1:].min()


data = [("calculate_statistics", None, None)]

sim_handler = SimulatorHandler()
sim_handler.num_instances = 5
sim_handler.show_ui = False
sim_handler.max_run_duration = 1000

#sim_handler.extract(data)

eps = ExperimentParameters.create_experiment_parameters(None, data)

n_data_points : dict[str, float] = {name : 0 for name in JOINT_NAMES}

positions : dict[str, list[float]] = {name : [] for name in JOINT_NAMES}
velocities : dict[str, list[float]] = {name : [] for name in JOINT_NAMES}
accelerations : dict[str, list[float]] = {name : [] for name in JOINT_NAMES}

for ep in eps:
    if not ep.extraction_path_full.with_suffix(".csv").exists():
        continue
    print(ep.extraction_path_full)
    df : pandas.DataFrame = pandas.read_csv(
        get_extraction_path_full(
            ep.action_name, ep.recording_date, ep.log_index).with_suffix(".csv"),
        sep=None, engine="python")
    dt = np.diff((df["time_step"] - df["time_step"][0]) / 1000)
    time_name = "time_step"
    for joint_name in JOINT_NAMES:
        jsd_name = "sensor_" + joint_name
        jr_name = "JR_A_" + joint_name
        joint_df = df[[jsd_name, jr_name, time_name]]
        indices = joint_df.index[abs(joint_df[jr_name]) == 200]
        if len(indices) == 0:
            continue
        start_index = indices[0]
        end_index = indices[-1]
        joint_df = joint_df[start_index:end_index] # remove data before and after experiments
        direction = [1 if abs(x) >= 199 else 0 for x in joint_df[jr_name].diff()] # find changes of JR [1,0..., 1,0,...]
        n_data_points[joint_name] = sum(direction) - 1
        dt = np.diff((joint_df["time_step"] - joint_df["time_step"][start_index]) / 1000)
        pos = joint_df[jsd_name].to_numpy()
        vel = np.diff(pos) / dt
        acc = np.diff(vel) / dt[1:]
        positions[joint_name].extend(list(pos))
        velocities[joint_name].extend(list(vel))
        accelerations[joint_name].extend(list(acc))
min_pos : dict[str, float] = {}
max_pos : dict[str, float] = {}
min_vel : dict[str, float] = {}
max_vel : dict[str, float] = {}
min_acc : dict[str, float] = {}
max_acc : dict[str, float] = {}
for joint_name in JOINT_NAMES:
    if len(positions[joint_name]) == 0:
        min_pos[joint_name] = float("nan")
        max_pos[joint_name] = float("nan")
        min_vel[joint_name] = float("nan")
        max_vel[joint_name] = float("nan")
        min_acc[joint_name] = float("nan")
        max_acc[joint_name] = float("nan")
        continue
    min_pos[joint_name] = np.percentile(positions[joint_name], 1)
    max_pos[joint_name] = np.percentile(positions[joint_name], 99)
    min_vel[joint_name] = np.percentile(velocities[joint_name], 1)
    max_vel[joint_name] = np.percentile(velocities[joint_name], 99)
    min_acc[joint_name] = np.percentile(accelerations[joint_name], 1)
    max_acc[joint_name] = np.percentile(accelerations[joint_name], 99)
max_pos_abs : dict[str, float] = {joint_name : max(abs(min_pos[joint_name]), max_pos[joint_name]) for joint_name in JOINT_NAMES}
max_vel_abs : dict[str, float] = {joint_name : max(abs(min_vel[joint_name]), max_vel[joint_name]) for joint_name in JOINT_NAMES}
max_acc_abs : dict[str, float] = {joint_name : max(abs(min_acc[joint_name]), max_acc[joint_name]) for joint_name in JOINT_NAMES}

dicts = {"data_points" : n_data_points,
         "min_pos" : min_pos,
         "max_pos" : max_pos,
         "max_pos_abs" : max_pos_abs,
         "min_vel" : min_vel,
         "max_vel" : max_vel,
         "max_vel_abs" : max_vel_abs,
         "min_acc" : min_acc,
         "max_acc" : max_acc,
         "max_acc_abs" : max_acc_abs}

df = pandas.DataFrame.from_dict(dicts, orient="index")
df.index.name = "statistic"

df["min"] = df.apply(np.nanmin, axis=1)
df["max"] = df.apply(np.nanmax, axis=1)
df.to_csv("statistics.csv")



