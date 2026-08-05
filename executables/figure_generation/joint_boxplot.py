from src import boxplot, SimulationParameters, SimulatorHandler, get_combined_data, action_shorthands, \
    SimulationGapData, JOINT_NAMES, SENSOR_NAMES, ABBREVIATIONS

identifier = "default"

r_kick_sensors = ["lShoulderPitch", "rShoulderPitch","lElbowYaw","rElbowYaw","rKneePitch","rAnklePitch","y_gyro"]
l_kick_sensors = ["lShoulderPitch", "rShoulderPitch","lElbowYaw","rElbowYaw","lKneePitch","lAnklePitch","y_gyro"]
r_kick_actions = ["kick_right"]
l_kick_actions = ["kick_left"]

walk_sensors = ['lElbowYaw','rElbowYaw','lHipPitch', 'rHipPitch', 'lKneePitch', 'rKneePitch', 'lAnklePitch', 'rAnklePitch', 'lAnkleRoll', 'rAnkleRoll']
walk_actions = ["walk_front", "walk_back","sidestep_left", "sidestep_right","turn_left", "turn_right"]

standup_sensors = ["lShoulderPitch","rShoulderPitch","lElbowYaw","rElbowYaw","lHipPitch", "rHipPitch", "lKneePitch","rKneePitch"]
standup_front_action = ["standup_front"]
standup_back_action = ["standup_back"]



def generate_plot(actions, sensors):
    data = get_combined_data()
    sim_params = SimulationParameters(identifier)
    sim_handler = SimulatorHandler()
    gap_handler = sim_handler.simulation_gap(sim_params, data)
    total_gap = gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES), actions)
    sensor_means = {"Comb." : total_gap}
    for sensor in SENSOR_NAMES:
        sensor_means[sensor] = gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [sensor]), actions)

    sensor_gaps = {"Comb." : []}
    for action in actions:
        for gap_data in gap_handler.get_all(action):
            sensor_gap = gap_data.get_total_gap_for_sensors(SENSOR_NAMES)
            for sensor in SENSOR_NAMES:
                key = ABBREVIATIONS[sensor]
                if key not in sensor_gaps.keys():
                    sensor_gaps[key] = []
                sensor_gaps[key].append(sensor_gap[sensor])
                sensor_gaps["Comb."].append(sensor_gap[sensor])


    boxplot(sensor_gaps,sensor_means ,
            "Joint", "Simulation Gap",
            identifier + "_"+ actions[0], h_line=total_gap, h_line_legend="all-joint gap: ",
            boxplot_sensors=list([ABBREVIATIONS[sensor] for sensor in sensors]))

generate_plot(r_kick_actions, r_kick_sensors)
generate_plot(l_kick_actions, l_kick_sensors)
generate_plot(walk_actions, walk_sensors)
generate_plot(standup_back_action, standup_sensors)
generate_plot(standup_front_action, standup_sensors)