from src import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
df = pd.read_csv(get_project_root() / "executables" / "optimization" / "full_run" / "2026_06_26_11_45_57" / "logbook.csv")

# Replace inf values with NaN so matplotlib can handle them cleanly
df["avg"] = df["avg"].replace([np.inf, -np.inf], np.nan)
df["min"] = df["min"].replace([np.inf, -np.inf], np.nan)
plt.figure(figsize=(6.06, 2.5))
df["avg"] = df["avg"] /  0.05307869684668788
df["min"] = df["min"] / 0.05307869684668788
df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna(subset=["avg"])
df = df.dropna(subset=["min"])
# Create the plot
plt.plot(df["gen"], df["avg"], linestyle="-", label="Average")
plt.plot(df["gen"], df["min"], linestyle="-", label="Minimum")
idx = df["min"].idxmin()
gen_min_pair = df.loc[idx, ["gen", "min"]]
plt.plot(gen_min_pair["gen"], gen_min_pair["min"], marker="o", label = "Global Minimum", color = "red")
plt.axhline(
    y=float(0.307),
    color="red",
    linestyle="--",
    linewidth=0.5,
    label= "base sim. gap: " + str(0.307)
)
plt.legend(loc="upper right")

# Add labels and title
plt.xlabel("Generation")
plt.ylabel("Simulation Gap")

# Optional: add grid
plt.grid(True)

# Show the plot
plt.savefig("optimized_0/training.pdf")

print(str(gen_min_pair))
param_name = "optimization_0"
settings = sim_params_from_file(get_project_root() / "executables" / "optimization" /"full_run"/ "2026_06_26_11_45_57" / "hallOfFame.csv", 3, "optimization_0")
settings.load_max_velocity()
settings.load_max_force(2.1)
sim_handler = SimulatorHandler()
gap_handler = sim_handler.simulation_gap(settings, get_test_data(), replay_mode=ExperimentMode.PARTIAL)
print(gap_handler.get_optimization_target())
gap_handler = sim_handler.simulation_gap(settings, get_train_data(), replay_mode=ExperimentMode.PARTIAL)
print(gap_handler.get_optimization_target())
gap_handler = sim_handler.simulation_gap(settings, get_combined_data(), replay_mode=ExperimentMode.PARTIAL)
print(gap_handler.get_optimization_target())
