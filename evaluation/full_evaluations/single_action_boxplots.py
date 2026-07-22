from src import *
import matplotlib.pyplot as plt
import numpy as np
from statistics import median
from matplotlib.cbook import boxplot_stats

folder = "testing"
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

# action gaps
excluded_sensors = ["headYaw", "headPitch", "lHipYawPitch"]
joints = [
"lShoulderPitch","lShoulderRoll","lElbowYaw","lElbowRoll","lWristYaw",
"rShoulderPitch","rShoulderRoll","rElbowYaw","rElbowRoll","rWristYaw",
"lHipRoll","lHipPitch","lKneePitch","lAnklePitch","lAnkleRoll",
"rHipYawPitch","rHipRoll","rHipPitch","rKneePitch","rAnklePitch","rAnkleRoll",
]
for action, gap_datas in gap_handler._sim_gap_data.items():
    sensor_gaps = {}
    total_gap = gap_handler.get_gap_avg([action], lambda x: SimulationGapData.get_total_gap_avg(x, joints))[action]
    for gap_data in gap_datas:
        if action == "standup_back" or action == "standup_front":
            sensor_gap = gap_data.get_total_gap_for_sensors(joints) # ignore gyro data
        else:
            sensor_gap = gap_data.get_total_gap_for_sensors()
        for key,value in sensor_gap.items():
            if key in excluded_sensors:
                continue
            if not key in sensor_gaps.keys():
                sensor_gaps[key] = []
            sensor_gaps[key].append(sensor_gap[key])
    top_n = dict(
        sorted(sensor_gaps.items(), key=lambda item: median(item[1]), reverse=True)[:10]
    )
    values = top_n.values()
    labels = [ABBREVIATIONS[key] for key in top_n.keys()]
    y_max = max([max(value) for value in top_n.values()])
    """
    for value, label in zip(sensor_gaps.values(), [ABBREVIATIONS[key] for key in sensor_gaps.keys()]):
        if np.nanmedian(value) > total_gap:
            values.append(value)
            labels.append(label)
            y_max = max(y_max, np.nanmax(value))
    """
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
        label= action + " mean: " + str(round(total_gap, 2))
    )
    plt.legend()
    plt.xticks()
    plt.savefig(folder + "/" + action + "_gaps.pdf", bbox_inches='tight')

    stats2 = boxplot_stats(values, labels=labels)
    # Convert to table
    table2 = pd.DataFrame([
        {
            "Label": s["label"],
            "Lower whisker": s["whislo"],
            "Q1": s["q1"],
            "Median": s["med"],
            "Mean": s["mean"],
            "Q3": s["q3"],
            "Upper whisker": s["whishi"]
        }
        for s in stats2
    ])
    table2.to_csv(folder +"/" + action + "statistics.csv", index=False)