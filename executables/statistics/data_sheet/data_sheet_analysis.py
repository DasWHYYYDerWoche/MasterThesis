import pandas as pd

# Load CSV
df = pd.read_csv("data_sheet.csv", index_col=0)

# Extract rows
no_load_speed = df.loc["No load speed avg (rpm)"].astype(float)
speed_tol = df.loc["No load speed tolerance (%)"].astype(float)
gear_ratio = df.loc["Speed Reduction Ratio"].astype(float)

# Max output speed in rpm (after gearbox)
max_output_rpm = (no_load_speed * (1 + speed_tol / 100)) / gear_ratio

# Convert rpm -> deg/s
max_output_deg_s = max_output_rpm * 6

result = pd.DataFrame({
    "MaxOutputSpeed_deg_per_s": max_output_deg_s
})
result.to_csv("data_sheet_analysis.csv")