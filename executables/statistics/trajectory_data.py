"""
This script counts all logs in the train and test folder and creates a csv stating how the data should be
distributed such that every action and robot has an independent 80 train/20 test split.

The results are saved to output_files/trajectory_data.csv
"""

from src import *
import pandas as pd

eps = ExperimentParameters.create_experiment_parameters("default_1", get_combined_data())
robot_1_total = {} # logs recorded on 260528
robot_2_total = {} # logs recorded on 260529
for ep in eps:
    action = ep.action_name
    date = ep.recording_date
    if date == "260528_0" or date == "260528_1":
        # log of robot 1
        if action not in robot_1_total.keys():
            robot_1_total[action] = 1
        else:
            robot_1_total[action] = robot_1_total[action]+1
    elif date == "260529_0" or date == "260529_1":
        if action not in robot_2_total.keys():
            robot_2_total[action] = 1
        else:
            robot_2_total[action] = robot_2_total[action]+1
robot_1_train = {}
robot_1_test = {}
robot_2_train = {}
robot_2_test = {}
for action in robot_2_total.keys():
    robot_1_train[action] = round(robot_1_total[action] * 0.8)
    robot_1_test[action] = robot_1_total[action] - robot_1_train[action]
    robot_2_train[action] = round(robot_2_total[action] * 0.8)
    robot_2_test[action] = robot_2_total[action] - robot_2_train[action]
combined_train = {action : robot_1_train[action] + robot_2_train[action] for action in robot_1_train}
combined_test = {action : robot_1_test[action] + robot_2_test[action] for action in robot_1_test}
combined_total = {action : robot_1_total[action] + robot_2_total[action] for action in robot_1_total}
results = {
    "robot_1_train" : robot_1_train,
    "robot_1_test" : robot_1_test,
    "robot_1_total" : robot_1_total,
    "robot_2_train" : robot_2_train,
    "robot_2_test" : robot_2_test,
    "robot_2_total" : robot_2_total,
    "combined_train" : combined_train,
    "combined_test" : combined_test,
    "combined_total" : combined_total,
}
for dic in results.values():
    dic["sum"] = sum(dic.values())

df = pd.DataFrame(results)
df.to_csv(PATH_OUTPUT / "trajectory_data.csv")