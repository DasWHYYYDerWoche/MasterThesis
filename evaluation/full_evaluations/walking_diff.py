from src import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from matplotlib.cbook import boxplot_stats
from statistics import median

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

data = get_combined_data()
sim_params_base = SimulationParameters("max_velocity")
sim_params_new = SimulationParameters("max_force_2.1")
sim_handler = SimulatorHandler()
gap_handler_base = sim_handler.simulation_gap(sim_params_base, data, replay_mode=ExperimentMode.PARTIAL)
gap_handler_new = sim_handler.simulation_gap(sim_params_new, data, replay_mode=ExperimentMode.PARTIAL)

folder = "maxForce"


plt.rcParams.update({
    "text.usetex": True,
    "font.size": 12,
    "font.family": "serif",
    "text.latex.preamble": r"""
        \usepackage{libertine}
        \usepackage[libertine]{newtxmath}
    """
})

sensors = ['lElbowYaw','rElbowYaw','lHipPitch', 'rHipPitch', 'lKneePitch', 'rKneePitch', 'lAnklePitch', 'rAnklePitch', 'lAnkleRoll', 'rAnkleRoll']
actions = ["walk_front", "walk_back","sidestep_left", "sidestep_right","turn_left", "turn_right"]
# kick right
sensor_gaps = {"combined" : []}
total_gap_base = gap_handler_base.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES), actions)
total_gap_new = gap_handler_new.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES), actions)
joint_gaps = {"combined" : total_gap_new - total_gap_base}
for joint in JOINT_NAMES:
    gap_base = gap_handler_base.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [joint]), actions)
    gap_new = gap_handler_new.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [joint]), actions)
    joint_gaps[joint] = gap_new - gap_base

for action in actions:
    for gap_data_base, gap_data_new in zip(gap_handler_base.get_all(action), gap_handler_new.get_all(action)):
        sensor_gap_base = gap_data_base.get_total_gap_for_sensors(JOINT_NAMES)
        sensor_gap_new = gap_data_new.get_total_gap_for_sensors(JOINT_NAMES)
        for key,base in sensor_gap_base.items():
            if key not in sensor_gaps.keys():
                sensor_gaps[key] = []
            sensor_gaps[key].append(sensor_gap_new[key] - base)
            sensor_gaps["combined"].append(sensor_gap_new[key] - base)

boxplot_gaps = {}
for sensor in sensors:
    boxplot_gaps[sensor] = sensor_gaps[sensor]

'''
sorted_data = dict(
    sorted(sensor_gaps.items(), key=lambda item: median(item[1]))
)
boxplot_gaps = dict(list(sorted_data.items())[:10])
'''
y_max = max([max(value) for value in boxplot_gaps.values()])
y_min = min([min(value) for value in boxplot_gaps.values()])
values = boxplot_gaps.values()
labels = [ABBREVIATIONS[key] for key in boxplot_gaps.keys()]
plt.figure(figsize=(6.06, 2.5))
plt.xlabel("Joint")
plt.ylabel("Simulation Gap Difference")
#plt.ylim(bottom=-y_min*y_margin, top=y_max*(1+y_margin))
plt.grid(visible=True, axis="y")
plt.boxplot(values, tick_labels=labels)
plt.axhline(
    y=float(joint_gaps["combined"]),
    color="red",
    linestyle="--",
    linewidth=0.5,
    label= "mean diff.: " + str(round(joint_gaps["combined"], 3))
)
plt.legend(loc="lower left")
plt.xticks()
plt.savefig(folder + "/" + "walking_motions_diff.pdf", bbox_inches='tight')

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
table2.to_csv(folder +"/" + "walking_motions_statistics_diff.csv", index=False)

