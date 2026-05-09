from __future__ import annotations

from collections import Counter
from typing import Optional
from pathlib import Path
import warnings


import numpy
import numpy as np
import pandas
from statistics import fmean
from enum import Enum

from pandas.errors import PerformanceWarning

from ..Constants import WEIGHTS, JOINT_NAMES, get_extraction_path_full, get_replay_path_full

import logging
logger = logging.getLogger("global_logger")

EXTRACTION_SUFFIX = "_extraction"
REPLAY_SUFFIX = "_replay"

class DataType(Enum):
    EXTRACTION = 0
    REPLAY = 1


class SimulationGapData:
    """
    can load extracted log and its replay to calculate various parts of the simulation gap
    """

    def __init__(self, param_set_id: str, action_name: str, recording_date: str, log_index: int,
                 pos_scale_factor : float = 1, vel_scale_factor : float = 1, acc_scale_factor : float = 1):
        self._merged : Optional[pandas.DataFrame] = None
        self._param_set_id: str = param_set_id
        self._action_name: str = action_name
        self._recording_date: str = recording_date
        self._log_index: int = log_index
        self._num_frames: int = -1
        self._dt = None
        self._pos_gap_factor = pos_scale_factor
        self._vel_gap_factor = vel_scale_factor
        self._acc_gap_factor = acc_scale_factor

    def load(self) -> bool:
        if self.loaded:
            return True
        path_replays: Path = get_replay_path_full(self._param_set_id, self._action_name, self._recording_date, self._log_index).parent
        #load extraction csv
        try:
            extraction : Optional[pandas.DataFrame] = pandas.read_csv(
                get_extraction_path_full(
                    self._action_name, self._recording_date, self._log_index).with_suffix(".csv"),
                sep=None, engine="python")
        except Exception as e:
            logger.error("No extraction at s% exist for log %s. Error: %s", path_replays, self._log_index, e)
            return False
        #load replay csv
        replay: Optional[pandas.DataFrame] = None
        replay_error = None
        for file in path_replays.iterdir():
            if file.name.startswith(str(self._log_index)):
                try:
                    replay = pandas.read_csv(path_replays / file.name, sep=None, engine="python")
                except Exception as e:
                    replay_error = e
                break
        if replay is None:
            logger.error("No replay at s% exist for log %s. Error: %s", path_replays, self._log_index, replay_error)
            return False
        # time column is not needed but gets automatically logged
        replay = replay.drop(columns=['time'])
        extraction = extraction.drop(columns=['time'])
        # merge on "time_step" and "replayed_frame"
        self._merged = pandas.merge(left=extraction, right=replay,
                                    left_on="time_step", right_on="replayed_frame",
                                    how='inner', suffixes=(EXTRACTION_SUFFIX, REPLAY_SUFFIX))
        self._merged.drop(columns=['replayed_frame'])
        # normalize and rename time column
        self._merged.rename(columns={"time_step_x": "time_step"}, inplace=True)
        self._merged['time_step'] = self._merged['time_step'] - self._merged['time_step'][0]
        self._num_frames = len(self._merged)
        self._dt = np.diff(self._merged['time_step'] / 1000)
        self._merged['sensor_x_gyro' + EXTRACTION_SUFFIX] = self._merged['sensor_x_gyro' + EXTRACTION_SUFFIX] - self._merged['sensor_x_gyro' + EXTRACTION_SUFFIX][0]
        self._merged['sensor_x_gyro' + REPLAY_SUFFIX] = self._merged['sensor_x_gyro' + REPLAY_SUFFIX] - self._merged['sensor_x_gyro' + REPLAY_SUFFIX][0]
        self._merged['sensor_y_gyro' + EXTRACTION_SUFFIX] = self._merged['sensor_y_gyro' + EXTRACTION_SUFFIX] - self._merged['sensor_y_gyro' + EXTRACTION_SUFFIX][0]
        self._merged['sensor_y_gyro' + REPLAY_SUFFIX] = self._merged['sensor_y_gyro' + REPLAY_SUFFIX] - self._merged['sensor_y_gyro' + REPLAY_SUFFIX][0]
        self._merged['sensor_z_gyro' + EXTRACTION_SUFFIX] = self._merged['sensor_z_gyro' + EXTRACTION_SUFFIX] - self._merged['sensor_z_gyro' + EXTRACTION_SUFFIX][0]
        self._merged['sensor_z_gyro' + REPLAY_SUFFIX] = self._merged['sensor_z_gyro' + REPLAY_SUFFIX] - self._merged['sensor_z_gyro' + REPLAY_SUFFIX][0]

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
        return list(self._merged['time_step'][start_index:end_index])

    # -------- gyro functions --------

    def _get_gyro_pos_extraction(self,
                                gyro_names : list[str],
                                start_index: int = 0,
                                end_index: int = -1) \
            -> dict[str, list[float]]:
        return self._integrate_all(self._get_gyro_vel_extraction(gyro_names, start_index, end_index))

    def _get_gyro_pos_replay(self,
                            gyro_names: list[str],
                            start_index: int = 0,
                            end_index: int = -1) \
            -> dict[str, list[float]]:
        return self._integrate_all(self._get_gyro_vel_replay(gyro_names, start_index, end_index))

    def _get_gyro_vel_extraction(self,
                                gyro_names: list[str],
                                start_index: int = 0,
                                end_index: int = -1) \
            -> dict[str, list[float]]:
        return self._get(EXTRACTION_SUFFIX, gyro_names, start_index,end_index)

    def _get_gyro_vel_replay(self,
                            gyro_names: list[str],
                            start_index: int = 0,
                            end_index: int = -1) \
            -> dict[str, list[float]]:
        return self._get(REPLAY_SUFFIX, gyro_names, start_index,end_index)

    def _get_gyro_acc_extraction(self,
                                gyro_names: list[str],
                                start_index: int = 0,
                                end_index: int = -1) \
            -> dict[str, list[float]]:
        return self._differentiate_all(self._get_gyro_vel_extraction(gyro_names, start_index, end_index))

    def _get_gyro_acc_replay(self,
                            gyro_names: list[str],
                            start_index: int = 0,
                            end_index: int = -1) \
            -> dict[str, list[float]]:
        return self._differentiate_all(self._get_gyro_vel_replay(gyro_names, start_index, end_index))

    # -------- get extraction/replay values --------

    def get_pos_extraction(self,
                           sensor_names: Optional[list[str]] = None,
                           start_index: int = 0,
                           end_index: int = -1) \
            -> dict[str, list[float]]:
        joint_names, gyro_names = self._split_sensor_names(sensor_names)
        return (self._get(EXTRACTION_SUFFIX, joint_names, start_index, end_index)
                | self._get_gyro_pos_extraction(gyro_names, start_index, end_index))

    def get_pos_replay(self,
                       sensor_names: Optional[list[str]] = None,
                       start_index: int = 0,
                       end_index: int = -1) \
            -> dict[str, list[float]]:
        joint_names, gyro_names = self._split_sensor_names(sensor_names)
        return (self._get(REPLAY_SUFFIX, joint_names, start_index, end_index)
                | self._get_gyro_pos_replay(gyro_names, start_index, end_index))

    def get_vel_extraction(self,
                           sensor_names: Optional[list[str]] = None,
                           start_index: int = 0,
                           end_index: int = -1) \
            -> dict[str, list[float]]:
        joint_names, gyro_names = self._split_sensor_names(sensor_names)
        return (self._differentiate_all(self.get_pos_extraction(joint_names, start_index, end_index))
                | self._get_gyro_vel_extraction(gyro_names, start_index, end_index))

    def get_vel_replay(self,
                       sensor_names: Optional[list[str]] = None,
                       start_index: int = 0,
                       end_index: int = -1) \
            -> dict[str, list[float]]:
        joint_names, gyro_names = self._split_sensor_names(sensor_names)
        return (self._differentiate_all(self.get_pos_replay(joint_names, start_index, end_index))
                | self._get_gyro_vel_replay(gyro_names, start_index, end_index))

    def get_acc_extraction(self,
                           sensor_names: Optional[list[str]] = None,
                           start_index: int = 0,
                           end_index: int = -1) \
            -> dict[str, list[float]]:
        joint_names, gyro_names = self._split_sensor_names(sensor_names)
        return (self._differentiate_all(self.get_pos_extraction(joint_names, start_index, end_index), n = 2)
                | self._get_gyro_acc_extraction(gyro_names, start_index, end_index))


    def get_acc_replay(self,
                       sensor_names: Optional[list[str]] = None,
                       start_index: int = 0,
                       end_index: int = -1) \
            -> dict[str, list[float]]:
        joint_names, gyro_names = self._split_sensor_names(sensor_names)
        return (self._differentiate_all(self.get_pos_replay(joint_names, start_index, end_index), n=2)
                | self._get_gyro_acc_replay(gyro_names, start_index, end_index))

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
            d_total[joint] = [(p + v + a)/3 for p,v,a in zip(d_p[joint], d_v[joint], d_a[joint])]
        return d_total

    # -------- average for joints --------

    def get_pos_gap_for_joints(self,
                               joint_names: Optional[list[str]] = None,
                               start_index: int = 0,
                               end_index: int = -1)\
            -> dict[str, float]:
        """
        Returns the average position sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : float(np.nanmean(sim_gaps)) for joint_name,sim_gaps in
                self.get_pos_gaps(joint_names, start_index, end_index).items()}

    def get_vel_gap_for_joints(self,
                               joint_names: Optional[list[str]] = None,
                               start_index: int = 0,
                               end_index: int = -1) \
            -> dict[str, float]:
        """
        Returns the average velocity sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : float(np.nanmean(sim_gaps)) for joint_name,sim_gaps in
                self.get_vel_gaps(joint_names, start_index, end_index).items()}

    def get_acc_gap_for_joints(self,
                               joint_names: Optional[list[str]] = None,
                               start_index: int = 0,
                               end_index: int = -1) \
            -> dict[str, float]:
        """
        Returns the average acceleration sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : float(np.nanmean(sim_gaps)) for joint_name, sim_gaps in
                self.get_acc_gaps(joint_names, start_index, end_index).items()}

    def get_total_gap_for_joints(self,
                                 joint_names: Optional[list[str]] = None,
                                 start_index: int = 0,
                                 end_index: int = -1) \
            -> dict[str, float]:
        """
        Returns the average total sim gap for the given joints by averaging over all given frames.
        """
        return {joint_name : float(np.nanmean(sim_gaps)) for joint_name,sim_gaps in
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
        return float(np.nanmean(self.get_pos_gap_for_frames(joint_names, start_index, end_index)))

    def get_vel_gap_avg(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        """
        Returns the velocity sim gap. Calculated by averaging over all given frames and joints
        """
        return float(np.nanmean(self.get_vel_gap_for_frames(joint_names, start_index, end_index)))

    def get_acc_gap_avg(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        """
        Returns the acceleration sim gap. Calculated by averaging over all given frames and joints
        """
        return float(np.nanmean(self.get_acc_gap_for_frames(joint_names, start_index, end_index)))

    def get_total_gap_avg(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        """
        Returns the total velocity sim gap. Calculated by averaging over all given frames and joints
        """
        return float(np.nanmean(self.get_total_gap_for_frames(joint_names, start_index, end_index)))

    # testing methods (these should yield the same result (apart from small rounding errors) as the ones above)

    def _get_pos_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        return self._get_weighted_joint_average_single(self.get_pos_gap_for_joints(joint_names, start_index, end_index))

    def _get_vel_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        return self._get_weighted_joint_average_single(self.get_vel_gap_for_joints(joint_names, start_index, end_index))

    def _get_acc_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        return self._get_weighted_joint_average_single(self.get_acc_gap_for_joints(joint_names, start_index, end_index))

    def _get_total_gap_avg_test(self, joint_names: Optional[list[str]] = None, start_index: int = 0, end_index: int = -1) -> float:
        return self._get_weighted_joint_average_single(self.get_total_gap_for_joints(joint_names, start_index, end_index))

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

    @property
    def sensor_names(self) -> list[str]:
        return JOINT_NAMES + ["x_gyro", "y_gyro", "z_gyro"]

    # -------- helper methods --------

    def _get(self,
             column_suffix : str,
             sensor_name: Optional[list[str]] = None,
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
        result : dict[str, list[float]] = {}
        for joint_name in sensor_name:
            result[joint_name] = ((self._merged["sensor_" + joint_name + column_suffix])[start_index:end_index]).to_list()
        return result

    def _calculate_gap(self,
                       d_extraction : dict[str, list[float]],
                       d_replay : dict[str, list[float]],
                       factor : float = 1) -> dict[str, list[float]]:
        gap = {}
        for joint_name in d_extraction.keys():
            gap[joint_name] = [pow((v_replay - v_extraction) / factor, 2)
                               for v_extraction, v_replay in zip(d_extraction[joint_name], d_replay[joint_name])]
        return gap

    def _get_weighted_joint_average(self, dictionary: dict[str, list[float]]) -> list[float]:
        return (numpy.average([dictionary[k] for k in dictionary.keys()],
                             weights=[WEIGHTS[k] for k in dictionary.keys()],
                             axis=0)
                .tolist()) # axis 0 = rows

    def _get_weighted_joint_average_single(self, dictionary: dict[str, float]) -> float:
        return (numpy.average([dictionary[k] for k in dictionary.keys()],
                             weights=[WEIGHTS[k] for k in dictionary.keys()],
                             axis=0)
                .tolist()) # axis 0 = rows

    def _split_sensor_names(self, sensor_names : list[str]) -> tuple[list[str], list[str]]:
        if sensor_names is None or len(sensor_names) == 0:
            return JOINT_NAMES, ["x_gyro", "y_gyro", "z_gyro"]
        gyro_names = []
        joint_names = []
        for name in sensor_names:
            if name.endswith("gyro"):
                gyro_names.append(name)
            else:
                joint_names.append(name)
        return joint_names, gyro_names

    def _differentiate(self, data : list[float], n : int = 1, pad_front : bool = True) -> list[float]:
        result = data
        for i in range(n):
            result = numpy.diff(result) / self._dt[i:]
        result = list(result)
        if pad_front:
            result = [float("nan") for _ in range(n)] + result
        return result

    def _differentiate_all(self, data : dict[str, list[float]], n : int = 1, pad_front : bool = True) -> dict[str, list[float]]:
        result = {}
        for key in data.keys():
            result[key] = self._differentiate(data[key], n, pad_front)
        return result

    def _integrate(self, data : list[float], n : int = 1, pad_front : bool = True) -> list[float]:
        result = data[1:]
        for i in range(n):
            result = numpy.cumsum(result * self._dt)
        result = list(result)
        if pad_front:
            result = [0] + result
        return list(result)

    def _integrate_all(self, data : dict[str, list[float]], n : int = 1, pad_front : bool = True) -> dict[str, list[float]]:
        result = {}
        for key in data.keys():
            result[key] = self._integrate(data[key], n, pad_front)
        return result