import math

import pandas as pd
gearbox_efficiency = 0.8

# Load CSV
df = pd.read_csv("input.csv", index_col=0)

# Extract rows
no_load_speed = df.loc["No load speed avg (rpm)"].astype(float)
speed_tol = df.loc["No load speed tolerance (%)"].astype(float)
gear_ratio = df.loc["Speed Reduction Ratio"].astype(float)
stall_torque = df.loc["Stall torque avg (mNm)"].astype(float)

# Max output speed in rpm (after gearbox)
max_output_rpm = (no_load_speed * (1 + speed_tol / 100)) / gear_ratio
# Convert rpm -> deg/s
max_deg_s = max_output_rpm * 6
max_rad_s = max_deg_s * math.pi / 180
sim_torque = stall_torque * gear_ratio * gearbox_efficiency / 1000

result = pd.DataFrame({
    "MaxSpeed_deg_per_s": max_deg_s,
    "MaxSpeed_rad_per_s": max_rad_s,
    "MaxTorque" : sim_torque
})
result.to_csv("output.csv")