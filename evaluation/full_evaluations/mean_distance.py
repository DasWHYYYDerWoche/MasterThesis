from src import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from matplotlib.cbook import boxplot_stats

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

folder = "maxVelocity"

data = get_combined_data()
sim_params_base = SimulationParameters("default_1")
sim_params_new = SimulationParameters("max_velocity")
sim_handler = SimulatorHandler()
gap_handler_base = sim_handler.simulation_gap(sim_params_base, data, replay_mode=ExperimentMode.PARTIAL)
gap_handler_new = sim_handler.simulation_gap(sim_params_new, data, replay_mode=ExperimentMode.PARTIAL)

good = []
bad = []
# action gaps
y_max = 0
y_min = 0
action_gaps_diff = {"combined" : []}
means = {"combined" : gap_handler_new.get_final_FINAL_gap_avg() - gap_handler_base.get_final_FINAL_gap_avg()}

for action, gap_datas_base  in gap_handler_base._sim_gap_data.items():
    action_gaps_diff[action] = []
    means[action] = gap_handler_new.get_final_FINAL_gap_avg(action_names = [action]) - gap_handler_base.get_final_FINAL_gap_avg(action_names = [action])
    gap_datas_new = gap_handler_new.get_all(action)
    for gap_data_base, gap_data_new in zip(gap_datas_base, gap_datas_new):
        gap_base = gap_data_base.get_total_gap_avg()
        gap_new = gap_data_new.get_total_gap_avg()
        gap_diff = gap_new- gap_base
        if gap_diff < 0:
            good.append(gap_diff)
        elif gap_diff > 0:
            bad.append(gap_diff)
        if gap_diff > y_max:
            y_max = gap_diff
        if gap_diff < y_min:
            y_min = gap_diff
        action_gaps_diff[action].append(gap_diff)
        action_gaps_diff["combined"].append(gap_diff)
print("good:")
print(len(good))
print(np.nanmean(good))
print(np.nanmedian(good))
print("bad:")
print(len(bad))
print(np.nanmean(bad))
print(np.nanmedian(bad))

plt.figure(figsize=(6.06, 2.5))
plt.ylim(y_min*(1+y_margin),y_max*(1+y_margin))
plt.xlabel("Action")
plt.ylabel("Simulation Gap Difference")
plt.grid(visible=True, axis="y")
values = action_gaps_diff.values()
labels = [action_shorthand[key] for key in action_gaps_diff.keys()]
plt.boxplot(values, tick_labels=labels)
plt.savefig(folder + "/diff_base.pdf", bbox_inches='tight')
stats2 = boxplot_stats(action_gaps_diff.values(), labels=action_gaps_diff.keys())
# Convert to table
table2 = pd.DataFrame([
    {
        "Label": action_shorthand[s["label"]],
        "Lower whisker": s["whislo"],
        "Q1": s["q1"],
        "Median": s["med"],
        "Mean": means[s["label"]],
        "Q3": s["q3"],
        "Upper whisker": s["whishi"]
    }
    for s in stats2
])
table2.to_csv(folder + "/diff_base.csv", index=False)