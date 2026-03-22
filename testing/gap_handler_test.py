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

def get_gap_avg_for_joints(gap_handler : SimulationGapHandler, action_name : str,
                    method : Callable[[SimulationGapData, Optional[list[str]], int, int], dict[str, float]],
                    start_frame: int,
                    end_frame: int,
                    line_type : str):
    data = gap_handler.get_gap_avg_for_joints(action_name, method, hinge_names = None, start_frame=start_frame, end_frame=end_frame)

    plt.figure(figsize=(20, 5))
    plt.title("value of " + method.__name__ + " for " + action_name)
    plt.xlabel("frame")
    plt.ylabel("pos/vel/acc (gap)")
    plt.plot([JOINT_SHORT[key] for key in data.keys()], data.values(), line_type, label=range(len(next(iter(data.values())))))
    plt.legend()
    plt.show()

def get_gap_avg_for_frames(gap_handler : SimulationGapHandler, action_name : str,
                    method : Callable[[SimulationGapData, Optional[list[str]], int, int],list[float]],
                    start_frame: int,
                    end_frame: int,
                    line_type : str):
    data = gap_handler.get_gap_avg_for_frames(action_name, method, hinge_names = None, start_frame=start_frame, end_frame=end_frame)

    plt.figure(figsize=(20, 5))
    plt.title("value of " + method.__name__ + " for " + action_name)
    plt.xlabel("frame")
    plt.ylabel("pos/vel/acc (gap)")
    plt.plot(range(len(data)), data, line_type, label=range(len(data[0])))
    plt.legend()
    plt.show()

