from src import *
import matplotlib.pyplot as plt
from typing import Callable

def get_all(gap_handler : SimulationGapHandler, action_name : str,
                    method : Callable[[SimulationGapData, Optional[list[str]], int, int], dict[str, list[float]]],
                    joint_name: str,
                    start_frame: int,
                    end_frame: int,
                    line_type : str):
    data = gap_handler.get_all(action_name, method, [joint_name], start_frame, end_frame)[joint_name]

    plt.figure(figsize=(20, 5))
    plt.title("value of " + method.__name__ + " for " + action_name + ", " + joint_name)
    plt.xlabel("frame")
    plt.ylabel("pos/vel/acc (gap)")
    plt.plot(range(len(data)), data, line_type, label=range(len(data[0])))
    plt.legend()
    plt.show()

def get_all_gap_avg_for_joints(gap_handler : SimulationGapHandler, action_name : str,
                               method : Callable[[SimulationGapData, Optional[list[str]], int, int], dict[str, float]],
                               start_frame: int,
                               end_frame: int,
                               line_type : str):
    data = gap_handler.get_all_gap_avg_for_joints(action_name, method, hinge_names = None, start_frame=start_frame, end_frame=end_frame)

    plt.figure(figsize=(20, 5))
    plt.title("value of " + method.__name__ + " for " + action_name)
    plt.xlabel("joints")
    plt.ylabel("pos/vel/acc (gap)")
    plt.plot([JOINT_SHORT[key] for key in data.keys()], data.values(), line_type, label=range(len(next(iter(data.values())))))
    plt.legend()
    plt.show()

def get_all_gap_avg_for_frames(gap_handler : SimulationGapHandler, action_name : str,
                               method : Callable[[SimulationGapData, Optional[list[str]], int, int],list[float]],
                               start_frame: int,
                               end_frame: int,
                               line_type : str):
    data = gap_handler.get_all_gap_avg_for_frames(action_name, method, hinge_names = None, start_frame=start_frame, end_frame=end_frame)

    plt.figure(figsize=(20, 5))
    plt.title("value of " + method.__name__ + " for " + action_name)
    plt.xlabel("frame")
    plt.ylabel("pos/vel/acc (gap)")
    plt.plot(range(len(data)), data, line_type, label=range(len(data[0])))
    plt.legend()
    plt.show()

def get_gap_avg_for_joints(gap_handler : SimulationGapHandler,
                           method: Callable[[SimulationGapData, Optional[list[str]], int, int], dict[str, float]],
                           start_frame: int,
                           end_frame: int,
                           line_type : str):
    gap = gap_handler.get_gap_avg_for_joints(None, method, start_frame=start_frame, end_frame=end_frame)

    plt.figure(figsize=(20, 5))
    plt.title("average value of " + method.__name__ + " for " + str(list(gap.keys())))
    plt.xlabel("joint")
    plt.ylabel("total gap")
    for action_name, dic_for_action in gap.items():
        plt.plot([JOINT_SHORT[key] for key in dic_for_action.keys()],dic_for_action.values(),  line_type, label=action_name)
    plt.legend()
    plt.show()

def get_gap_avg_for_frames(gap_handler : SimulationGapHandler,
                           method: Callable[[SimulationGapData, Optional[list[str]], int, int], list[float]],
                           start_frame: int,
                           end_frame: int,
                           line_type : str):
    gap = gap_handler.get_gap_avg_for_frames(None, method, start_frame=start_frame, end_frame=end_frame)

    plt.figure(figsize=(20, 5))
    plt.title("average value of " + method.__name__ + " for " + str(list(gap.keys())))
    plt.xlabel("frames")
    plt.ylabel("total gap")
    for action_name, list_for_action in gap.items():
        plt.plot(range(len(list_for_action)),list_for_action,  line_type, label=action_name)
    plt.legend()
    plt.show()