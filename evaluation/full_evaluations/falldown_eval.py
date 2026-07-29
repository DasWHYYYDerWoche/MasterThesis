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



sensors = ["lShoulderPitch","rShoulderPitch","lElbowYaw","rElbowYaw","lHipPitch", "rHipPitch", "lKneePitch","rKneePitch"]
# standup front
sensor_gaps = {}
total_gap = gap_handler.get_gap_avg(["standup_front"], lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES))["standup_front"]
combined = []
for gap_data in gap_handler.get_all("standup_front"):
    sensor_gap = gap_data.get_total_gap_for_sensors(JOINT_NAMES)
    for key,value in sensor_gap.items():
        if not key in sensor_gaps.keys():
            sensor_gaps[key] = []
        sensor_gaps[key].append(value)
        combined.append(value)
joint_gaps = {"combined" : total_gap}
for joint in JOINT_NAMES:
    joint_gaps[joint] = gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [joint]), ["standup_front"])
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
    label= "all-joint mean: " + str(round(total_gap, 3))
)
plt.legend(loc="lower left")
plt.xticks()
plt.savefig(folder + "/" + "standup_front" + "_gaps.pdf", bbox_inches='tight')
sensor_gaps["combined"] = combined
stats2 = boxplot_stats(sensor_gaps.values(), labels=sensor_gaps.keys())
# Convert to table
table2 = pd.DataFrame([
    {
        "Label": ABBREVIATIONS[s["label"]],
        "Lower whisker": round(s["whislo"],3),
        "Q1": round(s["q1"],3),
        "Median": round(s["med"],3),
        "Mean": round(joint_gaps[s["label"]],3),
        "Q3": round(s["q3"],3),
        "Upper whisker": round(s["whishi"],3)
    }
    for s in stats2
])
table2.to_csv(folder +"/" + "standup_front_" + "statistics.csv", index=False)






sensors = ["lShoulderPitch","rShoulderPitch","lElbowYaw","rElbowYaw","lHipPitch", "rHipPitch", "lKneePitch","rKneePitch"]
# standup back
sensor_gaps = {}
total_gap = gap_handler.get_gap_avg(["standup_back"], lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES))["standup_back"]
combined = []
for gap_data in gap_handler.get_all("standup_back"):
    sensor_gap = gap_data.get_total_gap_for_sensors(JOINT_NAMES)
    for key,value in sensor_gap.items():
        if not key in sensor_gaps.keys():
            sensor_gaps[key] = []
        sensor_gaps[key].append(value)
        combined.append(value)
joint_gaps = {"combined" : total_gap}
for joint in JOINT_NAMES:
    joint_gaps[joint] = gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [joint]), ["standup_back"])
boxplot_gaps = {}
for sensor in sensors:
    boxplot_gaps[sensor] = sensor_gaps[sensor]


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
    label= "all-joint mean: " + str(round(total_gap, 3))
)
plt.legend(loc="upper left")
plt.xticks()
plt.savefig(folder + "/" + "standup_back" + "_gaps.pdf", bbox_inches='tight')
sensor_gaps["combined"] = combined
stats2 = boxplot_stats(sensor_gaps.values(), labels=sensor_gaps.keys())
# Convert to table
table2 = pd.DataFrame([
    {
        "Label": ABBREVIATIONS[s["label"]],
        "Lower whisker": round(s["whislo"], 3),
        "Q1": round(s["q1"], 3),
        "Median": round(s["med"], 3),
        "Mean": round(joint_gaps[s["label"]], 3),
        "Q3": round(s["q3"], 3),
        "Upper whisker": round(s["whishi"], 3)
    }
    for s in stats2
])
table2.to_csv(folder +"/" + "standup_back_" + "statistics.csv", index=False)









