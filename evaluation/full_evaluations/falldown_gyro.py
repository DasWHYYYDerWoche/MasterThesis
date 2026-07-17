from src import *
import matplotlib.pyplot as plt
import numpy as np

folder = "maxForce"
param_name = "max_force_2.1"

data = get_combined_data()
sim_params = SimulationParameters(param_name)
sim_handler = SimulatorHandler()
gap_handler = sim_handler.simulation_gap(
    sim_params,
    data,
    replay_mode=ExperimentMode.PARTIAL,
)

plt.rcParams.update({
    "text.usetex": True,
    "font.size": 12,
    "font.family": "serif",
    "text.latex.preamble": r"""
        \usepackage{libertine}
        \usepackage[libertine]{newtxmath}
    """
})

# ------------------------------------------------------------------
# Collect trajectories
# ------------------------------------------------------------------
gaps = [
    np.asarray(gap_object.get_total_gap_for_frames(), dtype=float)
    for gap_object in gap_handler.get_all("standup_back")
]

if len(gaps) == 0:
    raise RuntimeError("No gap trajectories found.")

# Remove empty trajectories (optional but recommended)
gaps = [g for g in gaps if len(g) > 0]

if len(gaps) == 0:
    raise RuntimeError("All gap trajectories are empty.")

# ------------------------------------------------------------------
# Pad with NaNs so statistics ignore missing timesteps
# ------------------------------------------------------------------
max_len = max(len(g) for g in gaps)

padded = np.full((len(gaps), max_len), np.nan)

for i, g in enumerate(gaps):
    padded[i, :len(g)] = g

# ------------------------------------------------------------------
# Statistics over trajectories
# ------------------------------------------------------------------
with np.errstate(all="ignore"):
    min_gaps = np.nanmin(padded, axis=0)
    avg_gaps = np.nanmean(padded, axis=0)
    max_gaps = np.nanmax(padded, axis=0)

# Remove timesteps that have no data at all
valid = ~np.isnan(avg_gaps)

t = np.arange(np.count_nonzero(valid))

min_gaps = min_gaps[valid]
avg_gaps = avg_gaps[valid]
max_gaps = max_gaps[valid]

# ------------------------------------------------------------------
# Plot
# ------------------------------------------------------------------
plt.figure(figsize=(6.06, 2.5))

plt.fill_between(
    t,
    min_gaps,
    max_gaps,
    color="C0",
    alpha=0.2,
)

plt.plot(t, min_gaps, color="C0", linewidth=1, label="Minimum")
plt.plot(t, avg_gaps, color="C1", linewidth=2, label="Average")
plt.plot(t, max_gaps, color="C2", linewidth=1, label="Maximum")

# Axis limits
y_margin = 0.05
y_max = np.nanmax(max_gaps)

plt.ylim(-y_margin * y_max, y_max * (1 + y_margin))

plt.xlabel("Timestep")
plt.ylabel("Simulation Gap")
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig(f"{folder}/standup_back_gyro.pdf", bbox_inches="tight")


# ------------------------------------------------------------------
# Collect trajectories for front
# ------------------------------------------------------------------
gaps = [
    np.asarray(gap_object.get_total_gap_for_frames(), dtype=float)
    for gap_object in gap_handler.get_all("standup_front")
]

if len(gaps) == 0:
    raise RuntimeError("No gap trajectories found.")

# Remove empty trajectories (optional but recommended)
gaps = [g for g in gaps if len(g) > 0]

if len(gaps) == 0:
    raise RuntimeError("All gap trajectories are empty.")

# ------------------------------------------------------------------
# Pad with NaNs so statistics ignore missing timesteps
# ------------------------------------------------------------------
max_len = max(len(g) for g in gaps)

padded = np.full((len(gaps), max_len), np.nan)

for i, g in enumerate(gaps):
    padded[i, :len(g)] = g

# ------------------------------------------------------------------
# Statistics over trajectories
# ------------------------------------------------------------------
with np.errstate(all="ignore"):
    min_gaps = np.nanmin(padded, axis=0)
    avg_gaps = np.nanmean(padded, axis=0)
    max_gaps = np.nanmax(padded, axis=0)

# Remove timesteps that have no data at all
valid = ~np.isnan(avg_gaps)

t = np.arange(np.count_nonzero(valid))

min_gaps = min_gaps[valid]
avg_gaps = avg_gaps[valid]
max_gaps = max_gaps[valid]

# ------------------------------------------------------------------
# Plot
# ------------------------------------------------------------------
plt.figure(figsize=(6.06, 2.5))

plt.fill_between(
    t,
    min_gaps,
    max_gaps,
    color="C0",
    alpha=0.2,
)

plt.plot(t, min_gaps, color="C0", linewidth=1, label="Minimum")
plt.plot(t, avg_gaps, color="C1", linewidth=2, label="Average")
plt.plot(t, max_gaps, color="C2", linewidth=1, label="Maximum")

# Axis limits
y_margin = 0.05
y_max = np.nanmax(max_gaps)

plt.ylim(-y_margin * y_max, y_max * (1 + y_margin))

plt.xlabel("Timestep")
plt.ylabel("Simulation Gap")
plt.grid(True, alpha=0.3)
plt.legend(loc="upper right", bbox_to_anchor=(0.8, 1.0))

plt.tight_layout()
plt.savefig(f"{folder}/standup_front_gyro.pdf", bbox_inches="tight")
plt.show()