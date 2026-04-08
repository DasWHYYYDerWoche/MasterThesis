from __future__ import annotations
from typing import Optional
from pathlib import Path

import numpy
import numpy as np
import pandas
from statistics import fmean

from ..Constants import WEIGHTS, NAMES, get_extraction_path_full, get_replay_path_full

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
        self._num_frames: int = -1
        self.load()
        self._pos_gap_factor = 1
        self._vel_gap_factor = 1
        self._acc_gap_factor = 1

    def load(self) -> bool:
        if self.loaded:
            return True
        path_replays: Path = get_replay_path_full(self._param_set_id, self._action_name, self._recording_date, self._log_index).parent
        #load extraction csv
        extraction : Optional[pandas.DataFrame] = pandas.read_csv(
            get_extraction_path_full(
                self._action_name, self._recording_date, self._log_index).with_suffix(".csv"),
            sep=None, engine="python")
        if extraction is None:
            logger.error("No extraction at s% exist for log %s", path_replays, self._log_index)
            return False
        #load replay csv
        replay: Optional[pandas.DataFrame] = None
        for file in path_replays.iterdir():
            if file.name.startswith(str(self._log_index)):
                replay = pandas.read_csv(path_replays / file.name, sep=None, engine="python")
                break
        if replay is None:
            logger.error("No replay at s% exist for log %s", path_replays, self._log_index)
            return False
        #merge extraction and replay
        replay.drop(columns=['time'])
        self._merged = pandas.merge(left=extraction, right=replay, left_on="time", right_on="replayed_frame",
                                                how='inner')
        self._merged.drop(columns=['replayed_frame'])
        # correctly format time column
        self._merged.rename(columns={"time_x": "time"}, inplace=True)
        self._merged['time'] = self._merged['time'] - self._merged['time'][0]

        self._num_frames = len(self._merged)


        logger.info("Successfully loaded replays of log %s",
                    self._param_set_id + "," + self._action_name + "," + self._recording_date + "," + str(self._log_index))
        return True

    def unload(self):
        self._merged : Optional[pandas.DataFrame] = None
        self._num_frames = -1

    def get_time_steps(self, start_index: int = 0, end_index: int = -1) -> list[int]:
        if start_index < 0:
            start_index = 0
        if end_index == -1:
            end_index = len(self._merged.index)
        if start_index > end_index:
            return []
        return list(self._merged['time'])[start_index:end_index]

    # -------- get extraction/replay values --------

    def get_pos_extraction(self,
                           joint_names: Optional[list[str]] = None,
                           start_index: int = 0,
                           end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the joint positions of the extraction for the given joints and frames.
        """
        return self._get("_x", joint_names, start_index, end_index)

    def get_pos_replay(self,
                       joint_names: Optional[list[str]] = None,
                       start_index: int = 0,
                       end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the joint positions of the replay for the given joints and frames.
        """
        return self._get("_y", joint_names, start_index, end_index)

    def get_vel_extraction(self,
                           joint_names: Optional[list[str]] = None,
                           start_index: int = 0,
                           end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the angular velocities of the extraction for the given joints and frames.

        The velocity in step t is calculated as (p_{t+1} - p_{t-1}) / 2*step.
        v_0 is 0. v_T is approximated as (p_{T} - p_{T-1}) / step
        """
        return self._calculate_velocity("_x", joint_names, start_index, end_index)

    def get_vel_replay(self,
                       joint_names: Optional[list[str]] = None,
                       start_index: int = 0,
                       end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the angular velocities of the replay for the given joints and frames.

        The velocity in step t is calculated as (p_{t+1} - p_{t-1}) / 2*step.
        v_0 is 0. v_T is approximated as (p_{T} - p_{T-1}) / step
        """
        return self._calculate_velocity("_y", joint_names, start_index, end_index)

    def get_acc_extraction(self,
                           joint_names: Optional[list[str]] = None,
                           start_index: int = 0,
                           end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the angular accelerations of the extraction for the given joints and frames.

        The acceleration in step t is calculated as (v_{t+1} - v_{t-1}) / 2*step.
        a_0 is 0. a_T is approximated as (v_{T} - v_{T-1}) / step
        """
        return self._calculate_acceleration("_x", joint_names, start_index, end_index)


    def get_acc_replay(self,
                       joint_names: Optional[list[str]] = None,
                       start_index: int = 0,
                       end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the angular accelerations of the replay for the given joints and frames.

        The acceleration in step t is calculated as (v_{t+1} - v_{t-1}) / 2*step.
        a_0 is 0. a_T is approximated as (v_{T} - v_{T-1}) / step
        """
        return self._calculate_acceleration("_y", joint_names, start_index, end_index)

    # -------- partial gaps --------

    def get_pos_gaps(self,
                     joint_names: Optional[list[str]] = None,
                     start_index: int = 0,
                     end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the squared difference between the position of the extraction and replay for the given joints and frames
        """
        return self._calculate_gap(self.get_pos_extraction(joint_names, start_index, end_index),
                                   self.get_pos_replay(joint_names, start_index, end_index), self._pos_gap_factor)

    def get_vel_gaps(self,
                     joint_names: Optional[list[str]] = None,
                     start_index: int = 1, end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the squared difference between the velocity of the extraction and replay for the given joints and frames
        """
        return  self._calculate_gap(self.get_vel_extraction(joint_names, start_index, end_index),
                                   self.get_vel_replay(joint_names, start_index, end_index), self._vel_gap_factor)

    def get_acc_gaps(self,
                     joint_names: Optional[list[str]] = None,
                     start_index: int = 2,
                     end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the squared difference between the acceleration of the extraction and replay for the given joints and frames
        """
        return self._calculate_gap(self.get_acc_extraction(joint_names, start_index, end_index),
                                  self.get_acc_replay(joint_names, start_index, end_index), self._acc_gap_factor)

    def get_total_gaps(self,
                       joint_names: Optional[list[str]] = None,
                       start_index: int = 0,
                       end_index: int = -1) \
            -> dict[str, list[float]]:
        """
        Returns the sum of the pos, vel and acc gaps.
        """
        d_p = self.get_pos_gaps(joint_names, start_index, end_index)
        d_v = self.get_vel_gaps(joint_names, start_index, end_index)
        d_a = self.get_acc_gaps(joint_names, start_index, end_index)
        d_total = {}
        for joint in d_p.keys():
            l_p = d_p[joint]
            l_v = d_v[joint]
            l_a = d_a[joint]
            d_total[joint] = [p + v + a for p,v,a in zip(l_p, l_v, l_a)]
        return d_total

    # -------- average for joints --------

    def get_pos_gap_for_joints_TEST(self,
                                    joint_names: Optional[list[str]] = None,
                                    start_index: int = 0,
                                    end_index: int = -1)\
            -> dict[str, tuple[float, float]]:
        """
        Returns the average position sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : (float(np.average(sim_gaps)), float(np.std(sim_gaps))) for joint_name,sim_gaps in
                self.get_pos_gaps(joint_names, start_index, end_index).items()}

    def get_pos_gap_for_joints(self,
                               joint_names: Optional[list[str]] = None,
                               start_index: int = 0,
                               end_index: int = -1)\
            -> dict[str, float]:
        """
        Returns the average position sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : fmean(sim_gaps) for joint_name,sim_gaps in
                self.get_pos_gaps(joint_names, start_index, end_index).items()}

    def get_vel_gap_for_joints(self,
                               joint_names: Optional[list[str]] = None,
                               start_index: int = 0,
                               end_index: int = -1) \
            -> dict[str, float]:
        """
        Returns the average velocity sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : fmean(sim_gaps) for joint_name,sim_gaps in
                self.get_vel_gaps(joint_names, start_index, end_index).items()}

    def get_acc_gap_for_joints(self,
                               joint_names: Optional[list[str]] = None,
                               start_index: int = 0,
                               end_index: int = -1) \
            -> dict[str, float]:
        """
        Returns the average acceleration sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : fmean(sim_gaps) for joint_name,sim_gaps in
                self.get_acc_gaps(joint_names, start_index, end_index).items()}

    def get_total_gap_for_joints(self,
                                 joint_names: Optional[list[str]] = None,
                                 start_index: int = 0,
                                 end_index: int = -1) \
            -> dict[str, float]:
        """
        Returns the average total sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : fmean(sim_gaps) for joint_name,sim_gaps in
                self.get_total_gaps(joint_names, start_index, end_index).items()}

    # -------- average over all joints --------

    def get_pos_gap_for_frames(self,
                               joint_names: Optional[list[str]] = None,
                               start_index: int = 0,
                               end_index: int = -1) \
            -> list[float]:
        """
        Returns the average position sim gap in the given frames by averaging over all given joints.
        """
        return self._get_weighted_joint_average(self.get_pos_gaps(joint_names, start_index, end_index))

    def get_vel_gap_for_frames(self,
                               joint_names: Optional[list[str]] = None,
                               start_index: int = 0,
                               end_index: int = -1) \
            -> list[float]:
        """
        Returns the average velocity sim gap in the given frames by averaging over all given joints.
        """
        return self._get_weighted_joint_average(self.get_vel_gaps(joint_names, start_index, end_index))

    def get_acc_gap_for_frames(self,
                               joint_names: Optional[list[str]] = None,
                               start_index: int = 0,
                               end_index: int = -1) \
            -> list[float]:
        """
        Returns the average acceleration sim gap in the given frames by averaging over all given joints.
        """
        return self._get_weighted_joint_average(self.get_acc_gaps(joint_names, start_index, end_index))

    def get_total_gap_for_frames(self,
                                 joint_names: Optional[list[str]] = None,
                                 start_index: int = 0,
                                 end_index: int = -1) \
            -> list[float]:
        """
        Returns the average total sim gap in the given frames by averaging over all given joints.
        """
        return self._get_weighted_joint_average(self.get_total_gaps(joint_names, start_index, end_index))

    # -------- average over both joints and time --------

    def get_pos_gap_avg(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        """
        Returns the position sim gap. Calculated by averaging over all given frames and joints
        """
        return fmean(self.get_pos_gap_for_frames(joint_names, start_index, end_index))

    def get_vel_gap_avg(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        """
        Returns the velocity sim gap. Calculated by averaging over all given frames and joints
        """
        return fmean(self.get_vel_gap_for_frames(joint_names, start_index, end_index))

    def get_acc_gap_avg(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        """
        Returns the acceleration sim gap. Calculated by averaging over all given frames and joints
        """
        return fmean(self.get_acc_gap_for_frames(joint_names, start_index, end_index))

    def get_total_gap_avg(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        """
        Returns the total velocity sim gap. Calculated by averaging over all given frames and joints
        """
        return fmean(self.get_total_gap_for_frames(joint_names, start_index, end_index))

    # testing methods (these should yield the same result (apart from small rounding errors) as the ones above)

    def _get_pos_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        return fmean(self.get_pos_gap_for_joints(joint_names, start_index, end_index).values())

    def _get_vel_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        return fmean(self.get_vel_gap_for_joints(joint_names, start_index, end_index).values())

    def _get_acc_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        return fmean(self.get_acc_gap_for_joints(joint_names, start_index, end_index).values())

    def _get_total_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        return fmean(self.get_total_gap_for_joints(joint_names, start_index, end_index).values())

    # -------- utility methods --------

    def avg_abs_pos(self) -> float:
        extraction_max = fmean([fmean([abs(value) for value in values]) for values in self.get_pos_extraction().values()])
        replay_max = fmean([fmean([abs(value) for value in values]) for values in self.get_pos_replay().values()])
        return fmean([extraction_max, replay_max])

    def avg_abs_vel(self) -> float:
        extraction_max = fmean([fmean([abs(value) for value in values]) for values in self.get_vel_extraction().values()])
        replay_max = fmean([fmean([abs(value) for value in values]) for values in self.get_vel_replay().values()])
        return fmean([extraction_max, replay_max])

    def avg_abs_acc(self) -> float:
        extraction_max = fmean([fmean([abs(value) for value in values]) for values in self.get_acc_extraction().values()])
        replay_max = fmean([fmean([abs(value) for value in values]) for values in self.get_acc_replay().values()])
        return fmean([extraction_max, replay_max])

    def max_abs_pos(self) -> float:
        extraction_max = max([max([abs(value) for value in values]) for values in self.get_pos_extraction().values()])
        replay_max = max([max([abs(value) for value in values]) for values in self.get_pos_replay().values()])
        return max(extraction_max, replay_max)

    def max_abs_vel(self) -> float:
        extraction_max = max([max([abs(value) for value in values]) for values in self.get_vel_extraction().values()])
        replay_max = max([max([abs(value) for value in values]) for values in self.get_vel_replay().values()])
        return max(extraction_max, replay_max)

    def max_abs_acc(self) -> float:
        extraction_max = max([max([abs(value) for value in values]) for values in self.get_acc_extraction().values()])
        replay_max = max([max([abs(value) for value in values]) for values in self.get_acc_replay().values()])
        return max(extraction_max, replay_max)

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

    @property
    def num_frames(self):
        if not self.loaded:
            raise Exception("")
        return self._num_frames

    @property
    def pos_gap_factor(self):
        return self._pos_gap_factor

    @property
    def vel_gap_factor(self):
        return self._vel_gap_factor

    @property
    def acc_gap_factor(self):
        return self._acc_gap_factor

    @pos_gap_factor.setter
    def pos_gap_factor(self, value):
        self._pos_gap_factor = value

    @vel_gap_factor.setter
    def vel_gap_factor(self, value):
        self._vel_gap_factor = value

    @acc_gap_factor.setter
    def acc_gap_factor(self, value):
        self._acc_gap_factor = value

    # -------- helper methods --------

    def _get(self,
             column_name_extension : str,
             joint_names: Optional[list[str]] = None,
             start_index: int = 0,
             end_index: int = -1)\
            -> dict[str, list[float]]:
        if not self.loaded:
            logger.error("SimulationGapData must be loaded before calling any methods. %s", self.identifier)
        if start_index < 0:
            start_index = 0
        if end_index == -1:
            end_index = self.num_frames
        if start_index > end_index:
            return {}
        if joint_names is None or len(joint_names) <= 0:
            joint_names = NAMES
        result : dict[str, list[float]] = {}
        for joint_name in joint_names:
            result[joint_name] = ((self._merged["JSD_" + joint_name + column_name_extension])[start_index:end_index]).to_list()
        return result

    def _calculate_velocity(self,
                            column_name_extension : str,
                            joint_names: Optional[list[str]] = None,
                            start_index: int = 0,
                            end_index: int = -1)\
            -> dict[str, list[float]]:
        if not self.loaded:
            logger.error("SimulationGapData must be loaded before calling any methods. %s", self.identifier)
        if start_index < 0:
            start_index = 0
        if end_index == -1:
            end_index = len(self._merged.index)
        if start_index > end_index:
            return {}
        if joint_names is None or len(joint_names) <= 0:
            joint_names = NAMES
        result: dict[str, list[float]] = {}
        for joint_name in joint_names:
            positions = (self._merged["JSD_" + joint_name + column_name_extension]).to_numpy()
            frames = (self._merged["time"].to_numpy()) / 1000
            result[joint_name] = ([0] + (numpy.diff(positions) / numpy.diff(frames)).tolist())[start_index:end_index]
        return result

    def _calculate_acceleration(self,
                                column_name_extension : str,
                                joint_names: Optional[list[str]] = None,
                                start_index: int = 0,
                                end_index: int = -1)\
            -> dict[str, list[float]]:
        if not self.loaded:
            logger.error("SimulationGapData must be loaded before calling any methods. %s", self.identifier)
        if start_index < 0:
            start_index = 0
        if end_index == -1:
            end_index = len(self._merged.index)
        if start_index > end_index:
            return {}
        if joint_names is None or len(joint_names) <= 0:
            joint_names = NAMES
        result: dict[str, list[float]] = {}
        for joint_name in joint_names:
            positions = (self._merged["JSD_" + joint_name + column_name_extension]).to_numpy()
            frames = (self._merged["time"].to_numpy()) / 1000
            velocity = ((numpy.diff(positions) / numpy.diff(frames)).tolist())
            result[joint_name] = ([0,0] + (numpy.diff(velocity) / numpy.diff(frames[1:])).tolist())[start_index:end_index]
        return result

    def _calculate_gap(self, d_extraction :  dict[str, list[float]], d_replay :  dict[str, list[float]], factor : float = 1) -> dict[str, list[float]]:
        gap = {}
        for joint_name in d_extraction.keys():
            gap[joint_name] = [pow((p_replay - p_extraction)/factor, 2) for p_extraction, p_replay in zip(d_extraction[joint_name], d_replay[joint_name])]
        return gap

    def _get_weighted_joint_average(self, dictionary: dict[str, list[float]]) -> list[float]:
        keys = list(dictionary.keys())
        values_as_matrix = np.array([dictionary[k] for k in keys])  # shape: (n_keys, list_length)
        weights_as_matrix = np.array([WEIGHTS[k] for k in keys]) # shape: (n_keys, 1)
        return np.average(values_as_matrix, weights=weights_as_matrix, axis=0).tolist() # axis 0 = rows