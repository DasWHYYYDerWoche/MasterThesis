from src import boxplot, SimulationParameters, SimulatorHandler, get_combined_data, action_shorthands, \
    SimulationGapData, JOINT_NAMES, SENSOR_NAMES, ABBREVIATIONS

base_identifier = "max_velocity"
new_identifier = "max_force_2.2"

r_kick_sensors = ["lShoulderPitch", "rShoulderPitch","lElbowYaw","rElbowYaw","rKneePitch","rAnklePitch","y_gyro"]
l_kick_sensors = ["lShoulderPitch", "rShoulderPitch","lElbowYaw","rElbowYaw","lKneePitch","lAnklePitch","y_gyro"]
r_kick_actions = ["kick_right"]
l_kick_actions = ["kick_left"]

walk_sensors = ['lElbowYaw','rElbowYaw','lKneePitch', 'rKneePitch',"x_gyro","y_gyro","z_gyro"]
walk_actions = ["walk_front", "walk_back","sidestep_left", "sidestep_right","turn_left", "turn_right"]

standup_front_sensors = ["lShoulderPitch","rShoulderPitch","lElbowYaw","rElbowYaw", "lKneePitch","rKneePitch","x_gyro","y_gyro"]
standup_front_sensors_2 = ["lShoulderPitch","rShoulderPitch","lWristYaw","rWristYaw","lHipPitch", "lAnklePitch", "y_gyro"]
standup_back_sensors = ["lElbowYaw","rElbowYaw","lKneePitch","rKneePitch","x_gyro","y_gyro", "z_gyro"]
standup_back_sensors_2 = ["lShoulderPitch","rShoulderPitch","lHipYawPitch","x_gyro","y_gyro"]
standup_front_action = ["standup_front"]
standup_back_action = ["standup_back"]



def generate_plot(actions, sensors, outliers = None):
    data = get_combined_data()
    base_sim_params = SimulationParameters(base_identifier)
    new_sim_params = SimulationParameters(new_identifier)
    sim_handler = SimulatorHandler()
    base_gap_handler = sim_handler.simulation_gap(base_sim_params, data)
    new_gap_handler = sim_handler.simulation_gap(new_sim_params, data)
    base_total_gap = base_gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES), actions)
    new_total_gap = new_gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, JOINT_NAMES), actions)
    sensor_means = {"Comb." : new_total_gap - base_total_gap}
    for sensor in SENSOR_NAMES:
        base_gap = base_gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [sensor]), actions)
        new_gap = new_gap_handler.get_final_FINAL_gap_avg(lambda x: SimulationGapData.get_total_gap_avg(x, [sensor]), actions)
        sensor_means[sensor] = new_gap - base_gap

    sensor_gaps = {"Comb." : []}
    for action in actions:
        for base_gap_data, new_gap_data in zip(base_gap_handler.get_all(action), new_gap_handler.get_all(action)):
            if (base_gap_data.action_name is not new_gap_data.action_name or
                    base_gap_data.recording_date is not new_gap_data.recording_date or  base_gap_data.log_index is not new_gap_data.log_index):
                print("shit broken")

            base_sensor_gap = base_gap_data.get_total_gap_for_sensors(SENSOR_NAMES)
            new_sensor_gap = new_gap_data.get_total_gap_for_sensors(SENSOR_NAMES)
            for sensor in SENSOR_NAMES:
                key = ABBREVIATIONS[sensor]
                if key not in sensor_gaps.keys():
                    sensor_gaps[key] = []
                sensor_gaps[key].append(new_sensor_gap[sensor] - base_sensor_gap[sensor])
                sensor_gaps["Comb."].append(new_sensor_gap[sensor] - base_sensor_gap[sensor])


    boxplot(sensor_gaps, sensor_means,
            "Joint", "Simulation Gap Difference",base_identifier + "_" + new_identifier + "_" + actions[0],
            h_line=sensor_means["Comb."], h_line_legend="all-joint difference: ",
            boxplot_sensors=list([ABBREVIATIONS[sensor] for sensor in sensors]))

#generate_plot(r_kick_actions, r_kick_sensors)
#generate_plot(l_kick_actions, l_kick_sensors)
#generate_plot(walk_actions, walk_sensors)
generate_plot(standup_back_action, standup_back_sensors_2)
#generate_plot(standup_front_action, standup_front_sensors_2)