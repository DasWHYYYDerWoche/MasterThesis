from src import boxplot, SimulationParameters, SimulatorHandler, get_combined_data, action_shorthands
#max_force_2.2_home
base_identifier = "max_force_2.2"
new_identifier = "max_force_2.2_home"


data = get_combined_data()
base_sim_params = SimulationParameters(base_identifier)
new_sim_params = SimulationParameters(new_identifier)
sim_handler = SimulatorHandler()
base_gap_handler = sim_handler.simulation_gap(base_sim_params, data)
new_gap_handler = sim_handler.simulation_gap(new_sim_params, data)

simulation_gaps = {"Comb." : []}
mean_data = {"Comb." : new_gap_handler.get_optimization_target() - base_gap_handler.get_optimization_target()}
for action in base_gap_handler.actions:
    action_shorthand = action_shorthands[action]
    simulation_gaps[action_shorthand] = []
    mean_data[action_shorthand] = (new_gap_handler.get_final_FINAL_gap_avg(action_names=[action]) -
                                   base_gap_handler.get_final_FINAL_gap_avg(action_names=[action]))
    base_gap_data_for_action = base_gap_handler.get_all(action)
    new_gap_data_for_action = new_gap_handler.get_all(action)
    for base_gap_data, new_gap_data in zip(base_gap_data_for_action, new_gap_data_for_action):
        gap_diff = new_gap_data.get_total_gap_avg() - base_gap_data.get_total_gap_avg()
        simulation_gaps[action_shorthand].append(gap_diff)
        simulation_gaps["Comb."].append(gap_diff)

boxplot(simulation_gaps, mean_data,
        "Action", "Simulation Gap Difference", base_identifier + "_"+ new_identifier + "_comparison", y_margin=0.05)