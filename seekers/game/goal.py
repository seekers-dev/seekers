from __future__ import annotations

from .vector import *
from .config import *
from . import physical, player, camp

__all__ = [
    "Goal",
]


class Goal(physical.Physical):
    def __init__(self, scoring_time: float, base_thrust: float, *args, **kwargs):
        physical.Physical.__init__(self, *args, **kwargs)

        self.owner: player.Player | None = None
        self.time_owned: int = 0

        self.scoring_time = scoring_time
        self.base_thrust = base_thrust

    def thrust(self) -> float:
        return self.base_thrust

    @classmethod
    def from_config(cls, id_: str, position: Vector, config: Config) -> "Goal":
        return cls(
            scoring_time=config.goal_scoring_time,
            base_thrust=config.goal_thrust,
            id_=id_,
            position=position,
            velocity=Vector(0, 0),
            mass=config.goal_mass,
            radius=config.goal_radius,
            friction=config.goal_friction
        )

    def camp_tick(self, camp_: camp.Camp) -> bool:
        """Update the goal and return True if it has been captured."""
        if camp_.contains(self.position):
            if self.owner == camp_.owner:
                self.time_owned += 1
            else:
                self.time_owned = 0
                self.owner = camp_.owner

        return self.time_owned >= self.scoring_time
