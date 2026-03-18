from __future__ import annotations

class Hinge:
    """
    Representation of a Hinge of the NAO.
    """

    def __init__(self, max_velocity : float, max_force : float, p : float, i : float, d : float):
        self._max_velocity = max_velocity
        self._max_force = max_force
        self._p = p
        self._i = i
        self._d = d

    def to_dict(self) -> dict:
        return {
            "max_velocity": self._max_velocity,
            "max_force": self._max_force,
            "p": self._p,
            "i": self._i,
            "d": self._d,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Hinge":
        return cls(
            max_velocity=data["max_velocity"],
            max_force=data["max_force"],
            p=data["p"],
            i=data["i"],
            d=data["d"],
        )

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