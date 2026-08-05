import pandas as pd
from src import SimulatorHandler, SimulationParameters, get_combined_data, linear_plot, PATH_OUTPUT

sim_handler = SimulatorHandler()
data = get_combined_data()

df = pd.read_csv(PATH_OUTPUT / "max_force_search.csv", header=None)
df = df.drop(index=0)
df[0] = df[0].astype(float)
df[1] = df[1].astype(float)
search_results = dict(zip(df[0], df[1]))
"""

for gearbox_efficiency in [0.7,0.8,0.9,
                           1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,
                           2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9]:
    sim_params = SimulationParameters("max_force_" + str(gearbox_efficiency))
    search_results[gearbox_efficiency] = sim_handler.simulation_gap(sim_params, data).get_optimization_target()
pd.Series(search_results).to_csv(PATH_OUTPUT / "max_force_search.csv")
"""
default_gap = sim_handler.simulation_gap(SimulationParameters("max_velocity"), data).get_optimization_target()
linear_plot(
    x=list(search_results.keys()),
    y=list(search_results.values()),
    x_label="Gearbox Efficiency",
    y_label="Simulation Gap",
    path="images/max_force_search.pdf",
    h_line=default_gap,
    h_line_legend="Default Sim. Gap: ")