from src import *
import matplotlib.pyplot as plt
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

y_margin = 0.05
y_max = 0
motor_gaps = {}
for motor_type, joints in JOINT_TYPES_7.items():
    if len(joints) < 1:
        continue
    motor_gaps[motor_type] = []
    for gap_datas in gap_handler._sim_gap_data.values():
        for gap_data in gap_datas:
            gap = gap_data.get_total_gap_avg(joints)
            motor_gaps[motor_type].append(gap)
            if gap > y_max:
                y_max = gap

plt.figure(figsize=(6.06, 2.5))
plt.ylim(-y_max*y_margin, y_max*(1+y_margin))
plt.xlabel("Motor Index")
plt.ylabel("Simulation Gap")
plt.grid(visible=True, axis="y")
values = motor_gaps.values()
labels = list(motor_gaps.keys())
plt.boxplot(values, tick_labels=labels)
plt.savefig(folder + "/motor_gaps.pdf", bbox_inches='tight')
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
table2.to_csv(folder + "/motor_statistics.csv", index=False)
