from __future__ import annotations

HINGE_NAMES = [
"HeadYaw","HeadPitch",
"LShoulderPitch","LShoulderRoll","LElbowYaw","LElbowRoll","LWristYaw",
"RShoulderPitch","RShoulderRoll","RElbowYaw","RElbowRoll","RWristYaw",
"LHipYawPitch","LHipRoll","LHipPitch","LKneePitch","LAnklePitch","LAnkleRoll",
"RHipYawPitch","RHipRoll","RHipPitch","RKneePitch","RAnklePitch","RAnkleRoll"
]

class Hinge:
    def __init__(self, max_velocity : float, max_force : float, p : float, i : float, d : float):
        self._max_velocity = max_velocity
        self._max_force = max_force
        self._p = p
        self._i = i
        self._d = d

    @property
    def max_velocity(self) -> float:
        return self._max_velocity

    @property
    def max_force(self) -> float:
        return self._max_force

    @property
    def p(self) -> float:
        return self._p

    @property
    def i(self) -> float:
        return self._i

    @property
    def d(self) -> float:
        return self._d

    @max_velocity.setter
    def max_velocity(self, value: float) -> None:
        self._max_velocity = value

    @max_force.setter
    def max_force(self, value: float) -> None:
        self._max_force = value

    @p.setter
    def p(self, value: float) -> None:
        self._p = value

    @i.setter
    def i(self, value: float) -> None:
        self._i = value

    @d.setter
    def d(self, value: float) -> None:
        self._d = value

    def __str__(self):
        return ("H: " +
                str(self._max_velocity) + "," +
                str(self._max_force) + "," +
                str(self._p) + "," +
                str(self._i) + "," +
                str(self._d) + ",")