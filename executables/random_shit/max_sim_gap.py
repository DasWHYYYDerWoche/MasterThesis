from src import *

settings_default = SimulationParameters("default_1")
settings_max_vel = SimulationParameters("max_velocity")
settings_max_force = SimulationParameters("max_force_2.1")
settings_optimization_0 = SimulationParameters("optimization_0")
settings_optimization_1 = SimulationParameters("optimization_1")
settings_optimization_2 = SimulationParameters("optimization_2")
settings_optimization_3 = SimulationParameters("optimization_3")
settings_optimization_4 = SimulationParameters("optimization_4")

settings = [settings_default, settings_max_vel, settings_max_force,
            settings_optimization_0, settings_optimization_1, settings_optimization_2, settings_optimization_3, settings_optimization_4]
settings = [settings_default]
simulator = SimulatorHandler()
simulator.max_run_duration = 60
simulator.max_wait_for_ready = 60
simulator.dt = -1
simulator.show_ui = False


max_settings = None
max = 0
for setting in settings:
    print(setting._target_param_set_id)
    gap_handler = simulator.simulation_gap(setting, get_combined_data(),  replay_mode=ExperimentMode.PARTIAL)
    for gap_object in gap_handler.get_list():
        cur_gap = gap_object.get_total_gap_avg()
        if max < cur_gap:
            max = cur_gap
            max_settings = setting

print(max_settings._target_param_set_id)
print(max)