"""
calculates the max speed and force possible for the robots servo motor. Assumes the gearbox is 100% efficient
"""
from src import PATH_OUTPUT, PATH_INPUT
import math
import pandas as pd

df = pd.read_csv(PATH_INPUT / "motor_data.csv", index_col=0)
no_load_speed = df.loc["No load speed avg (rpm)"].astype(float)
speed_tol = df.loc["No load speed tolerance (%)"].astype(float)
gear_ratio = df.loc["Speed Reduction Ratio"].astype(float)
stall_torque = df.loc["Stall torque avg (mNm)"].astype(float)
torque_tol = df.loc["Stall torque tolerance (%)"].astype(float)

# Max output speed in rpm (after gearbox)
max_output_rpm = (no_load_speed * (1 + speed_tol / 100)) / gear_ratio
# rpm -> deg/s
max_deg_s = max_output_rpm * 360 / 60
max_rad_s = max_deg_s * math.pi / 180

# calculate torque (1000 for mNm to Nm), assume gearbox efficiency of 1
sim_torque = (stall_torque * (1 + torque_tol / 100)) * gear_ratio / 1000

result = pd.DataFrame({
    "MaxSpeed_deg_per_s": max_deg_s,
    "MaxSpeed_rad_per_s": max_rad_s,
    "MaxTorque" : sim_torque
})
result.to_csv(PATH_OUTPUT / "motor_limits.csv")