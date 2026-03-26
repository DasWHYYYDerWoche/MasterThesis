from __future__ import annotations

from typing import Optional

from ..Utils import SimulationGapData, ABBREVIATIONS
import matplotlib.pyplot as plt

class GapObjectVisualizer:
    def __init__(self, gap_object : SimulationGapData, fig_size : tuple[float,float] = (20,5)):
        self._gap_object = gap_object
        self._fig_size = fig_size
        self.load()

    def load(self) -> bool:
        return self._gap_object.load()

    def unload(self):
        self._gap_object.unload()

    def plt_extraction(self, joint_name : str, start_index : int = 0, end_index : int = -1, line_type : str = "-", unload : bool = False):
        x_axis = self._gap_object.get_time_steps(start_index, end_index)
        pos_extraction = self._gap_object.get_pos_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        vel_extraction = self._gap_object.get_vel_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        acc_extraction = self._gap_object.get_acc_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        if unload:
            self.unload()
        title = "The angle, angular velocity and acceleration of " + joint_name + "on the real robot for experiment \"" + self._gap_object.identifier + "\""
        y_label = "Position (degrees)/Velocity (?)/Acceleration (?)"
        self._plt_lists(x_axis,
                        [pos_extraction, vel_extraction, acc_extraction],
                        ["green", "red", "blue"],
                        ["Angle", "Velocity", "Acceleration"],
                        title, y_label, line_type)

    def plt_replay(self, joint_name : str, start_index : int = 0, end_index : int = -1, line_type : str = "-", unload : bool = False):
        x_axis = self._gap_object.get_time_steps(start_index, end_index)
        pos_replay = self._gap_object.get_pos_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        vel_replay = self._gap_object.get_vel_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        acc_replay = self._gap_object.get_acc_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        if unload:
            self.unload()
        title = "The angle, angular velocity and acceleration of " + joint_name + "on the simulated robot for experiment \"" + self._gap_object.identifier + "\""
        y_label = "Position (degrees)/Velocity (?)/Acceleration (?)"
        self._plt_lists(x_axis,
                        [pos_replay, vel_replay, acc_replay],
                        ["green", "red", "blue"],
                        ["Angle", "Velocity", "Acceleration"],
                        title, y_label, line_type)

    def plt_pos_gap(self, joint_name : str, start_index : int = 0, end_index : int = -1, line_type : str = "-", unload : bool = False):
        x_axis = self._gap_object.get_time_steps(start_index, end_index)
        pos_extraction = self._gap_object.get_pos_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        pos_replay = self._gap_object.get_pos_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        pos_gap = self._gap_object.get_pos_gaps(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        if unload:
            self.unload()
        title = "The angle of the " + joint_name + "for experiment \"" + self._gap_object.identifier + "\""
        y_label = "Position/Simulation Gap"
        self._plt_lists(x_axis,
                        [pos_extraction, pos_replay, pos_gap],
                        ["green", "red", "blue"],
                        ["Real Angle", "Simulator Angle", "Simulation Gap"],
                        title, y_label, line_type)

    def plt_vel_gap(self, joint_name : str, start_index : int = 0, end_index : int = -1, line_type : str = "-", unload : bool = False):
        x_axis = self._gap_object.get_time_steps(start_index, end_index)
        vel_extraction = self._gap_object.get_vel_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        vel_replay = self._gap_object.get_vel_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        vel_gap = self._gap_object.get_vel_gaps(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        if unload:
            self.unload()
        title = "The angular velocity of the " + joint_name + "for experiment \"" + self._gap_object.identifier + "\""
        y_label = "Velocity/Simulation Gap"
        self._plt_lists(x_axis,
                        [vel_extraction, vel_replay, vel_gap],
                        ["green", "red", "blue"],
                        ["Real Velocity", "Simulator Velocity", "Simulation Gap"],
                        title, y_label, line_type)

    def plt_acc_gap(self, joint_name : str, start_index : int = 0, end_index : int = -1, line_type : str = "-", unload : bool = False):
        x_axis = self._gap_object.get_time_steps(start_index, end_index)
        acc_extraction = self._gap_object.get_acc_extraction(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        acc_replay = self._gap_object.get_acc_replay(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        acc_gap = self._gap_object.get_acc_gaps(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        if unload:
            self.unload()
        title = "The angular acceleration of the " + joint_name + "for experiment \"" + self._gap_object.identifier + "\""
        y_label = "Acceleration/Simulation Gap"
        self._plt_lists(x_axis,
                        [acc_extraction, acc_replay, acc_gap],
                        ["green", "red", "blue"],
                        ["Real Acceleration", "Simulator Acceleration", "Simulation Gap"],
                        title, y_label, line_type)

    def plt_total_gap(self, joint_name : str, start_index : int = 0, end_index : int = -1, line_type : str = "-", unload : bool = False):
        x_axis = self._gap_object.get_time_steps(start_index, end_index)
        pos_gap = self._gap_object.get_pos_gaps(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        vel_gap = self._gap_object.get_vel_gaps(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        acc_gap = self._gap_object.get_acc_gaps(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        total_gap = self._gap_object.get_total_gaps(joint_names=[joint_name], start_index=start_index, end_index=end_index)[joint_name]
        if unload:
            self.unload()
        title = "Angle/Velocity/Acceleration and Accumulated Simulation Gap"
        y_label = "Sim Gap"
        self._plt_lists(x_axis,
                        [pos_gap, vel_gap, acc_gap, total_gap],
                        ["green", "red", "blue", "magenta"],
                        ["Position Gap", "Velocity Gap", "Acceleration Gap", "Accumulated Gap"],
                        title, y_label, line_type)

    def plt_avg_for_frames(self, joint_names : Optional[list[str]] = None, start_index : int = 0, end_index : int = -1, line_type : str = "-", unload : bool = False):
        x_axis = self._gap_object.get_time_steps(start_index, end_index)
        pos_gap = self._gap_object.get_pos_gap_for_frames(joint_names=joint_names, start_index=start_index, end_index=end_index)
        vel_gap = self._gap_object.get_vel_gap_for_frames(joint_names=joint_names, start_index=start_index, end_index=end_index)
        acc_gap = self._gap_object.get_acc_gap_for_frames(joint_names=joint_names, start_index=start_index, end_index=end_index)
        total_gap = self._gap_object.get_total_gap_for_frames(joint_names=joint_names, start_index=start_index, end_index=end_index)
        if unload:
            self.unload()
        title = ("Partial Simulation Gaps of \"" + self._gap_object.identifier + "\" averaged over " + (joint_names if joint_names else "all joints"))
        y_label = "Sim Gap"
        self._plt_lists(x_axis,
                        [pos_gap, vel_gap, acc_gap, total_gap],
                        ["green", "red", "blue", "magenta"],
                        ["Position Gap", "Velocity Gap", "Acceleration Gap", "Accumulated Gap"],
                        title, y_label, line_type)

    def plt_avg_for_joints(self, start_index : int = 0, end_index : int = -1, line_type : str = "o", unload : bool = False):
        pos_gap = self._gap_object.get_pos_gap_for_joints()
        vel_gap = self._gap_object.get_vel_gap_for_joints()
        acc_gap = self._gap_object.get_acc_gap_for_joints()
        total_gap = self._gap_object.get_total_gap_for_joints()
        if unload:
            self.unload()
        title = "Partial Simulation Gaps of each joint averaged over all frames."
        y_label = "Sim Gap"
        self._plt_dicts([pos_gap, vel_gap, acc_gap, total_gap],
                        ["green", "red", "blue", "magenta"],
                        ["Position Gap", "Velocity Gap", "Acceleration Gap", "Accumulated Gap"],
                        title, y_label, line_type)

    def _plt_lists(self, x_axis : list[float], data : list[list[float]], colors:list[str], labels:list[str],
                   title:str, y_label:str, line_type:str):
        plt.figure(figsize=self._fig_size)
        plt.title(title)
        plt.xlabel("Joint")
        plt.ylabel(y_label)
        plt.grid(visible=True)
        for i, d in enumerate(data):
            plt.plot(x_axis, d, line_type, color=colors[i], label=labels[i])
        plt.legend()
        plt.show()


    def _plt_dicts(self, data: list[dict[str, float]], colors:list[str], labels:list[str],
                   title:str, y_label:str, line_type:str):
        plt.figure(figsize=self._fig_size)
        plt.title(title)
        plt.xlabel("Joint")
        plt.ylabel(y_label)
        for i, dic in enumerate(data):
            plt.plot([ABBREVIATIONS[key] for key in dic.keys()], dic.values(), line_type, color=colors[i], label=labels[i])
        plt.legend()
        plt.show()