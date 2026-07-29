from src import *
import logging
logger = logging.getLogger("global_logger")
logging.basicConfig(filename='info.log',format='%(levelname)s: %(message)s', encoding='utf-8', filemode='w', level=logging.DEBUG)

data = get_combined_data()

sim_handler = SimulatorHandler()
sim_handler.num_instances = 8
sim_handler.replays_per_instance = 1
sim_handler.show_ui = False
sim_handler.dt = -1
sim_handler.max_wait_for_ready = 200
sim_handler.max_run_duration = 200

settings = SimulationParameters("max_velocity", "default")
#settings = sim_params_from_file(get_project_root() / "executables" / "optimization" /"full_run"/ "2026_06_26_11_45_57" / "hallOfFame.csv", 0, "optimization_4")
settings.load_max_velocity()
#settings.load_max_force()
settings.save_to_file()
sim_handler.replay(settings, data, mode = ExperimentMode.DEL_EXISTING)