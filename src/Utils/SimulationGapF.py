from __future__ import annotations

import subprocess
import time
from typing import Optional
from enum import Enum
import math
from pathlib import Path
from datetime import datetime

from .Constants import JOINT_DEFLECTIONS, HINGE_NAMES
from ..Utils import PATH_EXECUTABLE, ExperimentData, ExperimentType, PATH_LOG_EXTRACTION_SCENE, PATH_CSV_REPLAY_SCENE

import logging
logger = logging.getLogger("global_logger")

class SimulationGapF:
    """
    Simulation gap between a single replay file and the corresponding log
    """
    def __init__(self):
        self._absolute : dict[str, float] = dict.fromkeys(HINGE_NAMES, 0)
        self._relative_to_target : dict[str, float] = dict.fromkeys(HINGE_NAMES, 0)
        self._relative_to_range : dict[str, float] = dict.fromkeys(HINGE_NAMES, 0)
