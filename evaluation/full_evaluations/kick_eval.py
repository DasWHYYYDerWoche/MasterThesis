from src import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from matplotlib.cbook import boxplot_stats

folder = "default/actions"
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
y_margin = 0.05



sensors = ["lShoulderPitch", "rShoulderPitch","lElbowYaw","rElbowYaw","rKneePitch","rAnklePitch","y_gyro"]
# kick right
sensor_gaps = {}
combined = []
total_gap = gap_handler.get_gap_avg(["kick_right"], lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES))["kick_right"]
for gap_data in gap_handler.get_all("kick_right"):
    sensor_gap = gap_data.get_total_gap_for_sensors(JOINT_NAMES + ["y_gyro"])
    for key,value in sensor_gap.items():
        if not key in sensor_gaps.keys():
            sensor_gaps[key] = []
        sensor_gaps[key].append(sensor_gap[key])
        combined.append(sensor_gap[key])
joint_gaps = {"combined" : total_gap}
for joint in JOINT_NAMES + ["y_gyro"]:
    joint_gaps[joint] = gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [joint]), ["kick_right"])

boxplot_gaps = {}
for sensor in sensors:
    boxplot_gaps[sensor] = sensor_gaps[sensor]
y_max = max([max(value) for value in boxplot_gaps.values()])
values = boxplot_gaps.values()
labels = [ABBREVIATIONS[key] for key in boxplot_gaps.keys()]
plt.figure(figsize=(6.06, 2.5))
plt.xlabel("Joint")
plt.ylabel("Simulation Gap")
plt.ylim(bottom=-y_max*y_margin, top=y_max*(1+y_margin))
plt.grid(visible=True, axis="y")
plt.boxplot(values, tick_labels=labels)
plt.axhline(
    y=float(total_gap),
    color="red",
    linestyle="--",
    linewidth=0.5,
    label= "all-joint gap: " + str(round(total_gap, 3))
)
plt.legend(loc="upper left")
plt.xticks()
plt.savefig(folder + "/" + "kick_right" + "_gaps.pdf", bbox_inches='tight')
sensor_gaps["combined"] = combined
stats2 = boxplot_stats(sensor_gaps.values(), labels=sensor_gaps.keys())
# Convert to table
table2 = pd.DataFrame([
    {
        "Label": ABBREVIATIONS[s["label"]],
        "Lower whisker": s["whislo"],
        "Q1": s["q1"],
        "Median": s["med"],
        "Mean": joint_gaps[s["label"]],
        "Q3": s["q3"],
        "Upper whisker": s["whishi"]
    }
    for s in stats2
])
table2.to_csv(folder +"/" + "kick_right" + "statistics.csv", index=False)





sensors = ["lShoulderPitch", "rShoulderPitch","lElbowYaw","rElbowYaw","lKneePitch","lAnklePitch","y_gyro"]
# kick left
sensor_gaps = {}
combined = []
total_gap = gap_handler.get_gap_avg(["kick_left"], lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES))["kick_left"]
print(total_gap)
for gap_data in gap_handler.get_all("kick_left"):
    sensor_gap = gap_data.get_total_gap_for_sensors(JOINT_NAMES + ["y_gyro"])
    for key,value in sensor_gap.items():
        if not key in sensor_gaps.keys():
            sensor_gaps[key] = []
        sensor_gaps[key].append(sensor_gap[key])
        combined.append(sensor_gap[key])
joint_gaps = {"combined" : total_gap}
for joint in JOINT_NAMES + ["y_gyro"]:
    joint_gaps[joint] = gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [joint]), ["kick_left"])

boxplot_gaps = {}
for sensor in sensors:
    boxplot_gaps[sensor] = sensor_gaps[sensor]
y_max = max([max(value) for value in boxplot_gaps.values()])
values = boxplot_gaps.values()
labels = [ABBREVIATIONS[key] for key in boxplot_gaps.keys()]
plt.figure(figsize=(6.06, 2.5))
plt.xlabel("Joint")
plt.ylabel("Simulation Gap")
plt.ylim(bottom=-y_max*y_margin, top=y_max*(1+y_margin))
plt.grid(visible=True, axis="y")
plt.boxplot(values, tick_labels=labels)
plt.axhline(
    y=float(total_gap),
    color="red",
    linestyle="--",
    linewidth=0.5,
    label= "all-joint gap: 0.350"
)
plt.legend(loc="upper left")
plt.xticks()
plt.savefig(folder + "/" + "kick_left" + "_gaps.pdf", bbox_inches='tight')
sensor_gaps["combined"] = combined
stats2 = boxplot_stats(sensor_gaps.values(), labels=sensor_gaps.keys())
# Convert to table
table2 = pd.DataFrame([
    {
        "Label": ABBREVIATIONS[s["label"]],
        "Lower whisker": s["whislo"],
        "Q1": s["q1"],
        "Median": s["med"],
        "Mean": joint_gaps[s["label"]],
        "Q3": s["q3"],
        "Upper whisker": s["whishi"]
    }
    for s in stats2
])
table2.to_csv(folder +"/" + "kick_left" + "statistics.csv", index=False)