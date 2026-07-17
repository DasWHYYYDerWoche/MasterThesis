from src import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from statistics import median
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



sensors = ['lElbowYaw','rElbowYaw','lHipPitch', 'rHipPitch', 'lKneePitch', 'rKneePitch', 'lAnklePitch', 'rAnklePitch', 'lAnkleRoll', 'rAnkleRoll']
actions = ["walk_front", "walk_back","sidestep_left", "sidestep_right","turn_left", "turn_right"]
# kick right
sensor_gaps = {"combined" : []}
total_gap = gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES), actions)
joint_gaps = {"combined" : total_gap}
for joint in JOINT_NAMES:
    joint_gaps[joint] = gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [joint]), actions)

for action in actions:
    for gap_data in gap_handler.get_all(action):
        sensor_gap = gap_data.get_total_gap_for_sensors(JOINT_NAMES)
        for key,value in sensor_gap.items():
            if key not in sensor_gaps.keys():
                sensor_gaps[key] = []
            sensor_gaps[key].append(sensor_gap[key])
            sensor_gaps["combined"].append(sensor_gap[key])

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
print(total_gap)
plt.axhline(
    y=float(total_gap),
    color="red",
    linestyle="--",
    linewidth=0.5,
    label= "all-joint gap: " + str(round(total_gap, 3))
)
plt.legend(loc="upper left")
plt.xticks()
plt.savefig(folder + "/" + "walking_motions_gaps.pdf", bbox_inches='tight')

stats2 = boxplot_stats(sensor_gaps.values(), labels=sensor_gaps.keys())
# Convert to table
table2 = pd.DataFrame([
    {
        "Label": ABBREVIATIONS[s["label"]],
        "Lower whisker": round(s["whislo"],3),
        "Q1": round(s["q1"],3),
        "Median": round(s["med"],3),
        "Weighted Mean" : round(joint_gaps[s["label"]], 3),
        "Q3": round(s["q3"],3),
        "Upper whisker": round(s["whishi"],3)
    }
    for s in stats2
])
table2.to_csv(folder +"/" + "walking_motions_statistics.csv", index=False)

