from src import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from matplotlib.cbook import boxplot_stats

folder = "default"
param_name = "default_1"

data = get_combined_data()
sim_params = SimulationParameters(param_name)
sim_handler = SimulatorHandler()
gap_handler = sim_handler.simulation_gap(sim_params, data, replay_mode=ExperimentMode.PARTIAL)

plt.rcParams.update({
    "text.usetex": True,
    "font.size": 12,
    "font.family": "serif",
    "text.latex.preamble": r"""
        \usepackage{libertine}
        \usepackage[libertine]{newtxmath}
    """
})

# gyroscope scatterplot

y_margin = 0.05


y_max = 0
gyro_gaps: dict[str, list[float]] = {}
gyro_gap:dict[str,float] = {}
for action, gap_datas in gap_handler._sim_gap_data.items():
    gyro_gaps[action] = []
    gyro_gap[action] = gap_handler.get_final_FINAL_gap_avg(action_names=[action])
    for gap_data in gap_datas:
        gap = gap_data.get_total_gap_avg(
            sensor_names=["x_gyro", "y_gyro", "z_gyro"]
        )
        gyro_gaps[action].append(gap)
        y_max = max(y_max, gap)

plt.figure(figsize=(6.06, 2.0))

non_falldown_actions = ["kick_left", "kick_right",
                "walk_front", "walk_back",
                "sidestep_left", "sidestep_right",
                "turn_left", "turn_right"]
non_falldown_values = []
for action in non_falldown_actions:
    non_falldown_values.extend(gyro_gaps[action])
non_falldown_mean = np.nanmean(non_falldown_values)

labels = [action_shorthand[key] for key in gyro_gaps.keys()]
values = list(gyro_gaps.values())

plt.boxplot(
    values,
    labels=labels,
    showfliers=True,  # Set to False to hide outliers
)
plt.axhline(
    y=float(non_falldown_mean),
    color="red",
    linestyle="--",
    linewidth=0.5,
    label=f"non-standup mean: {round(non_falldown_mean,3)}"
)
plt.grid(visible=True, axis="y")
plt.ylim(-y_max * y_margin, y_max * (1 + y_margin))
plt.xlabel("Action")
plt.ylabel("Gyroscope Gap")
plt.legend()
plt.savefig(folder + "/gyroscope_boxplot.pdf", bbox_inches="tight")
stats1 = boxplot_stats(values, labels=labels)
# Convert to table
table1 = pd.DataFrame([
    {
        "Label": s["label"],
        "Lower whisker": s["whislo"],
        "Q1 / lower box": s["q1"],
        "Median": s["med"],
        "Weighted Mean": mean,
        "Q3 / upper box": s["q3"],
        "Upper whisker": s["whishi"]
    }
    for s, mean in zip(stats1, gyro_gap.values())
])
table1.to_csv(folder + "/gyroscope_statistics.csv", index=False)

# action gaps
y_max = 0
action_gaps = {"combined" : []}
action_gap = {"combined" : gap_handler.get_final_FINAL_gap_avg()}
for action, gap_datas in gap_handler._sim_gap_data.items():
    action_gaps[action] = []
    action_gap[action] = gap_handler.get_final_FINAL_gap_avg(action_names=[action])
    for gap_data in gap_datas:
        gap = gap_data.get_total_gap_avg()
        if gap > y_max:
            y_max = gap
        action_gaps[action].append(gap)
        action_gaps["combined"].append(gap)

plt.figure(figsize=(6.06, 2.5))
plt.ylim(-y_max*y_margin, y_max*(1+y_margin))
plt.xlabel("Action")
plt.ylabel("Simulation Gap")
plt.grid(visible=True, axis="y")
values = action_gaps.values()
labels = [action_shorthand[key] for key in action_gaps.keys()]
plt.boxplot(values, tick_labels=labels)
plt.savefig(folder + "/action_gaps.pdf", bbox_inches='tight')
stats2 = boxplot_stats(values, labels=labels)
# Convert to table
table2 = pd.DataFrame([
    {
        "Label": s["label"],
        "Lower whisker": s["whislo"],
        "Q1 / lower box": s["q1"],
        "Median": s["med"],
        "Weighted Mean": mean,
        "Q3 / upper box": s["q3"],
        "Upper whisker": s["whishi"]
    }
    for s, mean in zip(stats2, action_gap.values())
])
table2.to_csv(folder + "/action_statistics.csv", index=False)