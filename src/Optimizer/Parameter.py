"""
Defines a data object containing all information re
"""

from __future__ import annotations
import random
import numpy
from abc import abstractmethod, ABC
from typing import Optional
from ..Utils import SimulationParameters

class Parameter(ABC):
    """
    Data object that stores all information needed during the optimization, such as initialization mean/sigma and
    mutation mean/sigma.

    Subclasses need to implement the set method which updates the value in the given simulationParameters object.
    """

    def __init__(self,
                 name : str,
                 init_mu : float,
                 init_sigma : Optional[float] = None,
                 mutate_sigma : Optional[float] = None,
                 lower_bound : Optional[float] = None,
                 upper_bound : Optional[float] = None):
        self._name = name
        self._init_mu = init_mu
        self._init_sigma = init_sigma if init_sigma is not None else self._init_mu / 2
        self._mutate_sigma = mutate_sigma if mutate_sigma is not None else self._init_mu / 20
        self._lower_bound = lower_bound if lower_bound is not None else self._init_mu / 100
        self._upper_bound = upper_bound if upper_bound is not None else self._init_mu * 100

    def get_random_initial_value(self):
        value = random.gauss(self._init_mu, self._init_sigma)
        return numpy.clip(value, self._lower_bound, self._upper_bound)

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
                 motor_index : float,
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

kp = GlobalParameter("Kp", 12500)
kd = GlobalParameter("Kd", 10000)
contactKd = GlobalParameter("contactKd", 7.5)
contactKp = GlobalParameter("contactKp", 1425)

p0 = MotorParameter("p", 20, 0)
p1 = MotorParameter("p", 20, 1)
p2 = MotorParameter("p", 20, 2)
p3 = MotorParameter("p", 20, 3)
p4 = MotorParameter("p", 20, 4)
p25 = MotorParameter("p", 20, 2.5)

# d parameters have a fixed lower bound of 0 as this was their previous value in the simulator
d0 = MotorParameter("d", 0.3, 0, lower_bound=0)
d1 = MotorParameter("d", 0.3, 1, lower_bound=0)
d2 = MotorParameter("d", 0.3, 2, lower_bound=0)
d3 = MotorParameter("d", 0.3, 3, lower_bound=0)
d4 = MotorParameter("d", 0.3, 4, lower_bound=0)
d25 = MotorParameter("d", 0.3, 2.5, lower_bound=0)

#different sized parameter sets for the optimization. The thesis uses the last one.
PARAMETER_SET_0 = [kp, kd,contactKd, contactKp, p0,p1,p2,p3,p4]
PARAMETER_SET_1 = [kp, kd,contactKd, contactKp, p0,p1,p2,p3,p4, d0,d1,d2,d3,d4]
PARAMETER_SET_2 = [kp, kd,contactKd, contactKp, p0,p1,p2,p25,p3,p4, d0,d1,d2,d25,d3,d4]