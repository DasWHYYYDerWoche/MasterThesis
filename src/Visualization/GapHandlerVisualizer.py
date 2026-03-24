from __future__ import annotations

from typing import Optional, Callable

from .. import JOINT_SHORT
from ..Utils import SimulationGapHandler, SimulationGapData
from .GapObjectVisualizer import GapObjectVisualizer
import matplotlib.pyplot as plt

class GapHandlerVisualizer:
    def __init__(self, gap_handler : SimulationGapHandler):
        self._gap_handler : SimulationGapHandler = gap_handler
        self._figure_width = 20
        self._figure_height = 5

    def get_gap_object_visualizer(self, action_name : str, recording_date : str, log_index : int) -> GapObjectVisualizer:
        return GapObjectVisualizer(self._gap_handler.get(action_name, recording_date, log_index))

    def plt_all_for_action_joint(self, action_name: str,joint_name: str, f_name : str,
                                 method: Callable[[SimulationGapData], dict[str, list[float]]],
                                 line_type: str = "-"):
        plt.figure(figsize=(20, 5))
        plt.title("value of " + f_name + " for " + action_name + ", " + joint_name)
        plt.xlabel("frame")
        plt.ylabel("pos/vel/acc (gap)")
        for i, gap_object in enumerate(self._gap_handler.get_all(action_name)):
            gap_object.load()
            data = method(gap_object)[joint_name]
            plt.plot(gap_object.get_time_steps(), data, line_type, label=str(i))
            gap_object.unload()
        plt.legend()
        plt.show()

    def plt_all_gap_avg_for_joints(self, action_name: str, f_name : str,
                                 method: Callable[[SimulationGapData], dict[str, float]],
                                 line_type: str = "o"):
        plt.figure(figsize=(20, 5))
        plt.title("value of " + f_name + " for " + action_name + ", ")
        plt.xlabel("frame")
        plt.ylabel("pos/vel/acc (gap)")
        for i, gap_object in enumerate(self._gap_handler.get_all(action_name)):
            gap_object.load()
            data = method(gap_object)
            plt.plot([JOINT_SHORT[key] for key in data.keys()], data.values(), line_type, label=str(i))
            gap_object.unload()
        plt.legend()
        plt.show()

    def plt_all_gap_avg_for_frames(self, action_name: str,f_name : str,
                                   method: Callable[[SimulationGapData], list[float]],
                                   line_type: str = "_"):
        plt.figure(figsize=(20, 5))
        plt.title("value of " + f_name + " for " + action_name)
        plt.xlabel("frame")
        plt.ylabel("pos/vel/acc (gap)")
        for i, gap_object in enumerate(self._gap_handler.get_all(action_name)):
            gap_object.load()
            data = method(gap_object)
            plt.plot(gap_object.get_time_steps(), data, line_type, label=str(i))
            gap_object.unload()
        plt.legend()
        plt.show()

    def plt_gap_avg_for_joints(self,f_name : str,
                               method: Callable[[SimulationGapData], dict[str, float]],
                               line_type: str = "o"):
        gap = self._gap_handler.get_gap_avg_for_joints(None, method)

        plt.figure(figsize=(20, 5))
        plt.title("average value of " + f_name + " for " + str(list(gap.keys())))
        plt.xlabel("joint")
        plt.ylabel("total gap")
        for action_name, dic_for_action in gap.items():
            plt.plot([JOINT_SHORT[key] for key in dic_for_action.keys()], dic_for_action.values(), line_type,
                     label=action_name)
        plt.legend()
        plt.show()

    def plt_gap_avg_for_frames(self,f_name : str,
                               method: Callable[[SimulationGapData], list[float]],
                               line_type: str = "-"):
        gap = self._gap_handler.get_gap_avg_for_frames(None,method)
        plt.figure(figsize=(20, 5))
        plt.title("average value of " + f_name + " for " + str(list(gap.keys())))
        plt.xlabel("frames")
        plt.ylabel("total gap")
        for action_name, list_for_action in gap.items():
            plt.plot(range(len(list_for_action)), list_for_action, line_type, label=action_name)
        plt.legend()
        plt.show()