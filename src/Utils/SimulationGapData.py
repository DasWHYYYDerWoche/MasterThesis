from __future__ import annotations
from typing import Optional
from enum import Enum
from pathlib import Path
import pandas
from statistics import fmean

from .Constants import JOINT_WEIGHTS, JOINT_NAMES, get_extraction_path_full, get_replay_path_full

import logging
logger = logging.getLogger("global_logger")

class SimulationGapData:
    """
    can load extracted log and its replay to calculate various parts of the simulation gap
    """

    def __init__(self, param_set_id: str, action_name: str, recording_date: str, log_index: int):
        self._merged : Optional[pandas.DataFrame] = None
        self._param_set_id: str = param_set_id
        self._action_name: str = action_name
        self._recording_date: str = recording_date
        self._log_index: int = log_index

    def load(self) -> bool:
        path_replays: Path = get_replay_path_full(self._param_set_id, self._action_name, self._recording_date, self._log_index).parent
        #load extraction csv
        extraction : Optional[pandas.DataFrame] = pandas.read_csv(get_extraction_path_full(self._action_name, self._recording_date, self._log_index).with_suffix(".csv"),
                                           sep=None, engine="python")
        if extraction is None:
            logger.warning("No extraction at s% exist for log %s", path_replays, self._log_index)
            return False
        #load replay csv
        replay: Optional[pandas.DataFrame] = None
        for file in path_replays.iterdir():
            if file.name.startswith(str(self._log_index)):
                replay = pandas.read_csv(path_replays / file.name, sep=None, engine="python")
                break
        if replay is None:
            logger.warning("No replay at s% exist for log %s", path_replays, self._log_index)
            return False
        #merge extraction and replay
        replay.drop(columns=['time'])
        self._merged = pandas.merge(left=extraction, right=replay, left_on="time", right_on="replayed_frame",
                                                how='inner')
        self._merged.drop(columns=['replayed_frame'])
        logger.info("Successfully loaded replays of log %s",
                    self._param_set_id + "," + self._action_name + "," + self._recording_date + "," + str(self._log_index))
        return True

    def unload(self):
        self._merged : Optional[pandas.DataFrame] = None

    # -------- get extraction/replay values --------

    def get_pos_extraction(self,
                           joint_names: Optional[list[str]] = None,
                           start_frame: int = 0,
                           end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the joint positions of the extracted log for the given joints and frames.
        """
        return self._get("_x", joint_names, start_frame, end_frame)

    def get_pos_replay(self,
                       joint_names: Optional[list[str]] = None,
                       start_frame: int = 0,
                       end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the joint positions of the replayed log for the given joints and frames.
        """
        return self._get("_y", joint_names, start_frame, end_frame)

    def get_vel_extraction(self,
                           joint_names: Optional[list[str]] = None,
                           start_frame: int = 1,
                           end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the angular velocities of the extracted logs for the given joints and frames.
        """
        return self._get_derivative(self.get_pos_extraction(joint_names, start_frame - 1, end_frame), start_frame <= 0)

    def get_vel_replay(self,
                       joint_names: Optional[list[str]] = None,
                       start_frame: int = 1,
                       end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the angular velocities of the replayed logs for the given joints and frames.
        """
        return self._get_derivative(self.get_pos_replay(joint_names, start_frame - 1, end_frame), start_frame <= 0)

    def get_acc_extraction(self,
                           joint_names: Optional[list[str]] = None,
                           start_frame: int = 2,
                           end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the angular acceleration of the extracted logs for the given joints and frames.
        """
        return self._get_derivative(self.get_vel_extraction(joint_names, start_frame - 1, end_frame), start_frame <= 1)


    def get_acc_replay(self,
                       joint_names: Optional[list[str]] = None,
                       start_frame: int = 2,
                       end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the angular acceleration of the replayed logs for the given joints and frames.
        """
        return self._get_derivative(self.get_vel_replay(joint_names, start_frame - 1, end_frame), start_frame <= 1)

    # -------- partial gaps --------

    def get_pos_gap(self,
                    joint_names: Optional[list[str]] = None,
                    start_frame: int = 0,
                    end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the squared difference between the position of the extraction and replay for the given joints and frames
        """
        return self._get_partial_gap(self.get_pos_extraction(joint_names, start_frame, end_frame),
                                     self.get_pos_replay(joint_names, start_frame, end_frame))

    def get_vel_gap(self,
                    joint_names: Optional[list[str]] = None,
                    start_frame: int = 1, end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the squared difference between the velocity of the extraction and replay for the given joints and frames
        """
        return self._get_partial_gap(self.get_vel_extraction(joint_names, start_frame, end_frame),
                                     self.get_vel_replay(joint_names, start_frame, end_frame))

    def get_acc_gap(self,
                    joint_names: Optional[list[str]] = None,
                    start_frame: int = 2,
                    end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the squared difference between the acceleration of the extraction and replay for the given joints and frames
        """
        return self._get_partial_gap(self.get_acc_extraction(joint_names, start_frame, end_frame),
                                     self.get_acc_replay(joint_names, start_frame, end_frame))

    def get_total_gap(self,
                      joint_names: Optional[list[str]] = None,
                      start_frame: int = 0,
                      end_frame: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the sum of the pos, vel and acc gaps.
        """
        d_p = self.get_pos_gap(joint_names, start_frame, end_frame)
        d_v = self.get_vel_gap(joint_names, start_frame, end_frame)
        d_a = self.get_acc_gap(joint_names, start_frame, end_frame)
        d_total = {}
        for joint in d_p.keys():
            l_p = d_p[joint]
            l_v = d_v[joint]
            l_a = d_a[joint]
            d_total[joint] = [p + v + a for p,v,a in zip(l_p, l_v, l_a)]
        return d_total

    # -------- average for joints --------

    def get_pos_gap_avg_for_joints(self,
                                   joint_names: Optional[list[str]] = None,
                                   start_frame: int = 0,
                                   end_frame: int = -1)\
            -> dict[str, float]:
        """
        Returns the average position sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : fmean(sim_gaps) for joint_name,sim_gaps in
                self.get_pos_gap(joint_names, start_frame, end_frame).items()}

    def get_vel_gap_avg_for_joints(self,
                                   joint_names: Optional[list[str]] = None,
                                   start_frame: int = 0,
                                   end_frame: int = -1) \
            -> dict[str, float]:
        """
        Returns the average velocity sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : fmean(sim_gaps) for joint_name,sim_gaps in
                self.get_vel_gap(joint_names, start_frame, end_frame).items()}

    def get_acc_gap_avg_for_joints(self,
                                   joint_names: Optional[list[str]] = None,
                                   start_frame: int = 0,
                                   end_frame: int = -1) \
            -> dict[str, float]:
        """
        Returns the average acceleration sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : fmean(sim_gaps) for joint_name,sim_gaps in
                self.get_acc_gap(joint_names, start_frame, end_frame).items()}

    def get_total_gap_avg_for_joints(self,
                                     joint_names: Optional[list[str]] = None,
                                     start_frame: int = 0,
                                     end_frame: int = -1) \
            -> dict[str, float]:
        """
        Returns the average total sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : fmean(sim_gaps) for joint_name,sim_gaps in
                self.get_total_gap(joint_names, start_frame, end_frame).items()}

    # -------- average over all joints --------

    def get_pos_gap_avg_for_frames(self,
                                   joint_names: Optional[list[str]] = None,
                                   start_frame: int = 0,
                                   end_frame: int = -1) \
            -> list[float]:
        """
        Returns the average position sim gap in the given frames by averaging over all given joints.
        """
        return self._get_weighted_joint_average(self.get_pos_gap(joint_names, start_frame, end_frame))

    def get_vel_gap_avg_for_frames(self,
                                   joint_names: Optional[list[str]] = None,
                                   start_frame: int = 0,
                                   end_frame: int = -1) \
            -> list[float]:
        """
        Returns the average velocity sim gap in the given frames by averaging over all given joints.
        """
        return self._get_weighted_joint_average(self.get_vel_gap(joint_names, start_frame, end_frame))

    def get_acc_gap_avg_for_frames(self,
                                   joint_names: Optional[list[str]] = None,
                                   start_frame: int = 0,
                                   end_frame: int = -1) \
            -> list[float]:
        """
        Returns the average acceleration sim gap in the given frames by averaging over all given joints.
        """
        return self._get_weighted_joint_average(self.get_acc_gap(joint_names, start_frame, end_frame))

    def get_total_gap_avg_for_frames(self,
                                     joint_names: Optional[list[str]] = None,
                                     start_frame: int = 0,
                                     end_frame: int = -1) \
            -> list[float]:
        """
        Returns the average total sim gap in the given frames by averaging over all given joints.
        """
        return self._get_weighted_joint_average(self.get_total_gap(joint_names, start_frame, end_frame))

    # -------- average over both joints and time --------

    def get_pos_gap_avg(self, joint_names: Optional[list[str]] = None, start_frame: int = 0, end_frame: int = -1) -> float:
        """
        Returns the position sim gap. Calculated by averaging over all given frames and joints
        """
        return fmean(self.get_pos_gap_avg_for_frames(joint_names, start_frame, end_frame))

    def get_vel_gap_avg(self, joint_names: Optional[list[str]] = None, start_frame: int = 0, end_frame: int = -1) -> float:
        """
        Returns the velocity sim gap. Calculated by averaging over all given frames and joints
        """
        return fmean(self.get_vel_gap_avg_for_frames(joint_names, start_frame, end_frame))

    def get_acc_gap_avg(self, joint_names: Optional[list[str]] = None, start_frame: int = 0, end_frame: int = -1) -> float:
        """
        Returns the acceleration sim gap. Calculated by averaging over all given frames and joints
        """
        return fmean(self.get_acc_gap_avg_for_frames(joint_names, start_frame, end_frame))

    def get_total_gap_avg(self, joint_names: Optional[list[str]] = None, start_frame: int = 0, end_frame: int = -1) -> float:
        """
        Returns the total velocity sim gap. Calculated by averaging over all given frames and joints
        """
        return fmean(self.get_total_gap_avg_for_frames(joint_names, start_frame, end_frame))

    # testing methods (these should yield the same result (apart from small rounding errors) as the ones above)

    def _get_pos_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_frame: int = 0, end_frame: int = -1) -> float:
        return fmean(self.get_pos_gap_avg_for_joints(joint_names, start_frame, end_frame).values())

    def _get_vel_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_frame: int = 0, end_frame: int = -1) -> float:
        return fmean(self.get_vel_gap_avg_for_joints(joint_names, start_frame, end_frame).values())

    def _get_acc_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_frame: int = 0, end_frame: int = -1) -> float:
        return fmean(self.get_acc_gap_avg_for_joints(joint_names, start_frame, end_frame).values())

    def _get_total_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_frame: int = 0, end_frame: int = -1) -> float:
        return fmean(self.get_total_gap_avg_for_joints(joint_names, start_frame, end_frame).values())

    # -------- properties --------

    @property
    def identifier(self) -> str:
        return self._param_set_id + ";" + self._action_name + ";" + self._recording_date + ";" + str(self._log_index)

    @property
    def param_set_id(self) -> str:
        return self._param_set_id

    @property
    def action_name(self) -> str:
        return self._action_name

    @property
    def recording_date(self) -> str:
        return self._recording_date

    @property
    def log_index(self) -> int:
        return self._log_index

    @property
    def loaded(self) -> bool:
        return self._merged is not None

    # -------- helper methods --------

    def _get(self,
             column_name_extension : str,
             joint_names: Optional[list[str]] = None,
             start_frame: int = 0,
             end_frame: int = -1)\
            -> dict[str, list[float]]:
        if start_frame < 0:
            start_frame = 0
        if end_frame == -1:
            end_frame = len(self._merged.index)
        if start_frame > end_frame:
            return {}
        if joint_names is None or len(joint_names) <= 0:
            joint_names = JOINT_NAMES
        dic = {joint_name : [] for joint_name in joint_names}
        for joint_name in joint_names:
            dic[joint_name] = ((self._merged["JSD_" + joint_name + column_name_extension])[start_frame:end_frame]).to_list()
        return dic

    def _get_derivative(self, dic : dict[str, list[float]], add_zero_prefix : bool) -> dict[str, list[float]]:
        for key in dic.keys():
            value = dic[key]
            value = [p1 - p0 for p0,p1 in zip(value[:-1], value[1:])]
            if add_zero_prefix:
                value = [0] + value
            dic[key] = value
        return dic

    def _get_partial_gap(self, d_extraction :  dict[str, list[float]], d_replay :  dict[str, list[float]]):
        gap = {}
        for joint_name in d_extraction.keys():
            gap[joint_name] = [pow(p_replay - p_extraction, 2) for p_extraction, p_replay in zip(d_extraction[joint_name], d_replay[joint_name])]
        return gap

    def _get_weighted_joint_average(self, dic: dict[str, list[float]]) -> list[float]:
        num_key = len(dic.keys())
        joint_sums = [0 for _ in range(len(next(iter(dic.values()))))]
        for key in dic.keys():
            joint_sums = list(map(lambda x,y:x+(JOINT_WEIGHTS[key]*y), joint_sums, dic[key]))
        return [joint_avg / num_key for joint_avg in joint_sums]