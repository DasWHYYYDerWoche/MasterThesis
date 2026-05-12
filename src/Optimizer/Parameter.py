from __future__ import annotations

import random
from abc import abstractmethod, ABC
from typing import Optional

from ..Utils import SimulationParameters

class Parameter(ABC):
    def __init__(self,
                 name : str,
                 init_mu : float,
                 init_sigma : Optional[float] = None,
                 mutate_sigma : Optional[float] = None,
                 lower_bound : Optional[float] = None,
                 upper_bound : Optional[float] = None):
        self._name = name
        self._init_mu = init_mu
        self._init_sigma = init_sigma if init_sigma is not None else self._init_mu / 5
        self._mutate_sigma = mutate_sigma if mutate_sigma is not None else self._init_mu / 10
        self._lower_bound = lower_bound if lower_bound is not None else self._init_mu / 10
        self._upper_bound = upper_bound if upper_bound is not None else self._init_mu * 10

    def get_random_initial_value(self):
        return random.gauss(self._init_mu, self._init_sigma)

    def identifier(self) -> str:
        return self._name

    @abstractmethod
    def set(self, value, simulation_parameters : SimulationParameters):
        pass

    @property
    def name(self):
        return self._name

    @property
    def init_mu(self):
        return self._init_mu

    @property
    def init_sigma(self):
        return self._init_sigma

    @property
    def mutate_sigma(self):
        return self._mutate_sigma

    @property
    def lower_bound(self):
        return self._lower_bound

    @property
    def upper_bound(self):
        return self._upper_bound

class GlobalParameter(Parameter):
    def __init__(self,
                 name : str,
                 init_mu : float,
                 init_sigma : Optional[float] = None,
                 mutate_sigma : Optional[float] = None,
                 lower_bound: Optional[float] = None,
                 upper_bound: Optional[float] = None):
        super().__init__(name, init_mu, init_sigma, mutate_sigma, lower_bound, upper_bound)

    def set(self, value, simulation_parameters : SimulationParameters):
        setattr(simulation_parameters, self._name, value)

class MotorParameter(Parameter):
    def __init__(self,
                 name : str,
                 init_mu : float,
                 motor_index : int,
                 init_sigma : Optional[float] = None,
                 mutate_sigma : Optional[float] = None,
                 lower_bound: Optional[float] = None,
                 upper_bound: Optional[float] = None):
        super().__init__(name, init_mu, init_sigma, mutate_sigma, lower_bound, upper_bound)
        self._motor_index = motor_index

    def set(self, value, simulation_parameters : SimulationParameters):
        simulation_parameters.set_for_joint_type(self._motor_index, self._name, value)

    def identifier(self) -> str:
        return self._name + str(self._motor_index)

PARAMETERS_GLOBAL_0 = ["Kd", "Kp", "contactKd"]
PARAMETERS_PER_TYPE_0 = ["p"]
PARAMETERS_PER_JOINT_0 = []


PARAMETERS_GLOBAL_1 = ["Kd", "Kp", "contactKd"]
PARAMETERS_PER_TYPE_1 = ["p", "d"]
PARAMETERS_PER_JOINT_1 = []

kp = GlobalParameter("Kp", 12500)
kd = GlobalParameter("Kd", 10000)
contactKd = GlobalParameter("contactKd", 7.5)

p0 = MotorParameter("p", 20, 0)
p1 = MotorParameter("p", 20, 1)
p2 = MotorParameter("p", 20, 2)
p3 = MotorParameter("p", 20, 3)
p4 = MotorParameter("p", 20, 4)

d0 = MotorParameter("d", 0, 0, 2, 1, -100, 100)
d1 = MotorParameter("d", 0, 1, 2, 1, -100, 100)
d2 = MotorParameter("d", 0, 2, 2, 1, -100, 100)
d3 = MotorParameter("d", 0, 3, 2, 1, -100, 100)
d4 = MotorParameter("d", 0, 4, 2, 1, -100, 100)

PARAMETER_SET_0 = [kp, kd,contactKd, p0,p1,p2,p3,p4]
PARAMETER_SET_1 = [kp, kd,contactKd, p0,p1,p2,p3,p4, d0,d1,d2,d3,d4]