from __future__ import annotations

from src import SimulatorHandler, ExperimentParameters, get_extraction_path_full, NAMES
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

sim_handler.extract(data)

eps = ExperimentParameters.create_experiment_parameters(None, data)

data_points : dict[str, float] = {name : 0 for name in NAMES}
min_pos : dict[str, float] = {name : 1000 for name in NAMES}
max_pos : dict[str, float] = {name : -1000 for name in NAMES}
min_vel : dict[str, float] = {name : 1000 for name in NAMES}
max_vel : dict[str, float] = {name : -1000 for name in NAMES}
min_acc : dict[str, float] = {name : 1000 for name in NAMES}
max_acc : dict[str, float] = {name : -1000 for name in NAMES}
#TODO max force

for ep in eps:
    df : pandas.DataFrame = pandas.read_csv(
        get_extraction_path_full(
            ep.action_name, ep.recording_date, ep.log_index).with_suffix(".csv"),
        sep=None, engine="python")
    dt = np.diff((df["time_step"] - df["time_step"][0]) / 1000)
    for joint_name in NAMES:
        jr_iter = iter(df["JR_A_" + joint_name])
        jr_cur = next(jr_iter, None)
        start_angle = None
        search_angle = None
        while jr_cur is not None and start_angle is None:
            if jr_cur == 200:
                start_angle = 200
                search_angle = -200
            elif jr_cur == -200:
                start_angle = -200
                search_angle = 200
            jr_cur = next(jr_iter, None)
        while jr_cur is not None:
            if jr_cur == search_angle:
                data_points[joint_name] += 1
                search_angle = start_angle
                start_angle = jr_cur
            jr_cur = next(jr_iter, None)
        pos = df["JSD_" + joint_name]
        vel = np.diff(pos) / dt
        acc = np.diff(vel) / dt[1:]
        min_pos[joint_name] = min(min_pos[joint_name], min(pos))
        max_pos[joint_name] = max(max_pos[joint_name], max(pos))
        min_vel[joint_name] = min(min_vel[joint_name], min(vel))
        max_vel[joint_name] = max(max_vel[joint_name], max(vel))
        min_acc[joint_name] = min(min_acc[joint_name], min(acc))
        max_acc[joint_name] = max(max_acc[joint_name], max(acc))

max_pos_abs : dict[str, float] = {joint_name : max(abs(min_pos[joint_name]), max_pos[joint_name]) for joint_name in NAMES}
max_vel_abs : dict[str, float] = {joint_name : max(abs(min_vel[joint_name]), max_vel[joint_name]) for joint_name in NAMES}
max_acc_abs : dict[str, float] = {joint_name : max(abs(min_acc[joint_name]), max_acc[joint_name]) for joint_name in NAMES}

dicts = {"data_points" : data_points,
         "min_pos" : min_pos,
         "max_pos" : max_pos,
         "max_pos_abs" : max_pos_abs,
         "min_vel" : min_vel,
         "max_vel" : max_vel,
         "max_vel_abs" : max_vel_abs,
         "min_acc" : min_acc,
         "max_acc" : max_acc,
         "max_acc_abs" : max_acc_abs}

func_map = {"data_points" : lambda x : None,
         "min_pos" : f_min,
         "max_pos" : f_max,
         "max_pos_abs" : f_max,
         "min_vel" : f_min,
         "max_vel" : f_max,
         "max_vel_abs" : f_max,
         "min_acc" : f_min,
         "max_acc" : f_max,
         "max_acc_abs" : f_max}

df = pandas.DataFrame.from_dict(dicts, orient="index")
df.index.name = "statistic"

df["min"] = df.apply(min, axis=1)
df["max"] = df.apply(max, axis=1)
df.to_csv("statistics.csv")



