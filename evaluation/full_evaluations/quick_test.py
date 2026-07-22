from src import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
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
excluded_sensors = ["headYaw", "headPitch", "lHipYawPitch", "x_gyro", "y_gyro", "z_gyro"]
y_max = 0
for action, gap_datas in gap_handler._sim_gap_data.items():
    sensor_gaps = {}
    for gap_data in gap_datas:
        sensor_gap = gap_data.get_total_gap_for_sensors()
        for key,value in sensor_gap.items():
            if key in excluded_sensors:
                continue
            if not key in sensor_gaps.keys():
                sensor_gaps[key] = []
            sensor_gaps[key].append(sensor_gap[key])
            if sensor_gap[key] > y_max:
                y_max = sensor_gap[key]

    print(action)
    plt.figure(figsize=(6.06, 2.5))
    plt.xlabel("Joint")
    plt.ylabel("Simulation Gap")
    plt.ylim(bottom=0, top=1.5)
    plt.grid(visible=True, axis="y")
    plt.boxplot(sensor_gaps.values(), tick_labels=[ABBREVIATIONS[key] for key in sensor_gaps.keys()])
    plt.xticks(rotation=45, ha="right")
    plt.savefig(folder + "/" + action + "_gaps.pdf", bbox_inches='tight')
