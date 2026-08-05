from src import boxplot, SimulationParameters, SimulatorHandler, get_combined_data, action_shorthands, SimulationGapData

identifier = "default"
name_addon = "gyroscope"
sensor_names = ["x_gyro", "y_gyro", "z_gyro"]

data = get_combined_data()
sim_params = SimulationParameters(identifier)
sim_handler = SimulatorHandler()
gap_handler = sim_handler.simulation_gap(sim_params, data)

simulation_gaps = {"Comb." : []}
mean_data = {"Comb." : gap_handler.get_final_FINAL_gap_avg(lambda gap_object: SimulationGapData.get_total_gap_avg(gap_object,sensor_names=sensor_names))}
for action in gap_handler.actions:
    action_shorthand = action_shorthands[action]
    simulation_gaps[action_shorthand] = []
    mean_data[action_shorthand] = gap_handler.get_final_FINAL_gap_avg(action_names=[action])
    gap_data_for_action = gap_handler.get_all(action)
    for gap_data in gap_data_for_action:
        gap = gap_data.get_total_gap_avg(sensor_names=sensor_names)
        simulation_gaps[action_shorthand].append(gap)
        simulation_gaps["Comb."].append(gap)

boxplot(simulation_gaps,mean_data , "Action", "Simulation Gap", identifier + "_" + name_addon)