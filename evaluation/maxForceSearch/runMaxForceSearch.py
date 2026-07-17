import matplotlib.pyplot as plt
from src import *
y_margin = 0.05

x = [0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9]
y = [0.032861844485424466,
     0.02717532568852249,
     0.027337114442422143,
     0.02622647238521709,
     0.025491234535537945,
     0.025679654621886445,
     0.020933531299071183,
     0.01935908729083381,
     0.018722348489987852,
     0.0192555076107004,
     0.018668773066535232,
     0.01831858846422718,
     0.017864301958727766,
     0.017845775240346536,
     0.017687793628725582,
     0.01772306811753273,
     0.017791555340992377,
     0.017771573665919176,
     0.01777260811737439,
     0.017807639816462082,
     0.017868765975882106,
     0.017923484595750248,
     0.017840563341151888]
#y = [data / 0.05307869684668788 for data in y]
y = []

for epsilon in x:
    sim_params = SimulationParameters("max_force_" + str(epsilon))
    sim_handler = SimulatorHandler()
    gap_handler = sim_handler.simulation_gap(sim_params, get_combined_data(), replay_mode=ExperimentMode.PARTIAL)
    gap = gap_handler.get_optimization_target()
    y.append(gap)
min_y = min(y)
max_y = max(y)
min_x = x[y.index(min_y)]
data = get_combined_data()
sim_params = SimulationParameters("default_1")
sim_handler = SimulatorHandler()
gap_handler = sim_handler.simulation_gap(sim_params, data, replay_mode=ExperimentMode.PARTIAL)
gap = gap_handler.get_optimization_target()

plt.rcParams.update({
    "text.usetex": True,
    "font.size": 12,
    "font.family": "serif",
    "text.latex.preamble": r"""
        \usepackage{libertine}
        \usepackage[libertine]{newtxmath}
    """
})
plt.figure(figsize=(6.06, 2.5))
plt.plot(x, y, marker='o')
plt.plot(min_x, min_y, marker='o')
plt.xlabel("Gearbox Efficiency Factor")
plt.ylabel("Simulation Gap")
plt.axhline(
        y=float(gap),
        color="red",
        linestyle="--",
        linewidth=0.5,
        label= "Default Sim. Gap: " + str(round(gap, 3))
    )
plt.legend()
plt.ylim(-y_margin * max_y,(y_margin + 1) * max_y)
plt.grid(True)
plt.savefig("outputMaxForceSearch.pdf", bbox_inches='tight')