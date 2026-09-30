"""A small, deterministic game engine for the Take It Back campaign.

The engine keeps game rules separate from the CLI so a future graphical client
can use the same shelter, combat, and territory mechanics.
"""

from dataclasses import dataclass, field
from enum import Enum


class Duty(str, Enum):
    TRAIN = "train"
    EAT = "eat"
    SLEEP = "sleep"
    FIGHT = "fight"


@dataclass
class Civilian:
    name: str
    health: int = 100
    readiness: int = 0
    hunger: int = 0
    duty: Duty = Duty.TRAIN

    def advance(self, duty: Duty) -> None:
        self.duty = duty
        if duty is Duty.TRAIN:
            self.readiness = min(100, self.readiness + 8)
        elif duty is Duty.EAT:
            self.hunger = max(0, self.hunger - 30)
        elif duty is Duty.SLEEP:
            self.health = min(100, self.health + 5)
            self.hunger = min(100, self.hunger + 5)
        elif duty is Duty.FIGHT:
            self.hunger = min(100, self.hunger + 10)


@dataclass
class Shelter:
    civilians: list[Civilian]
    food: int = 100
    airtight: bool = True
    breached: bool = False
    day: int = 0

    def rotate(self) -> Duty:
        """Advance one day and rotate every civilian to the next duty."""
        duties = list(Duty)
        for civilian in self.civilians:
            next_duty = duties[(duties.index(civilian.duty) + 1) % len(duties)]
            civilian.advance(next_duty)
        self.food = max(0, self.food - len(self.civilians))
        self.day += 1
        return self.civilians[0].duty if self.civilians else Duty.TRAIN

    def breach_lock(self, attackers: int = 1) -> int:
        """Open the shelter lock and return the number of Devoured inside."""
        if attackers < 1:
            raise ValueError("attackers must be positive")
        if not self.airtight:
            return 0
        self.airtight = False
        self.breached = True
        return attackers

    @property
    def fighting_strength(self) -> int:
        return sum(
            civilian.readiness
            for civilian in self.civilians
            if civilian.health > 0
        )


@dataclass
class Territory:
    name: str
    devoured: int
    reclaimed: bool = False


@dataclass
class Campaign:
    shelter: Shelter
    territories: list[Territory]
    devoured_in_shelter: int = 0

    def survive_day(self) -> None:
        self.shelter.rotate()
        if self.shelter.food == 0:
            for civilian in self.shelter.civilians:
                civilian.hunger = min(100, civilian.hunger + 15)

    def defend_shelter(self) -> bool:
        """Fight the Devoured inside the shelter.

        A civilian can defeat one attacker for every 50 readiness points.
        Casualties are applied only when the defenders are overwhelmed.
        """
        if not self.shelter.breached:
            return False
        defenders = self.shelter.fighting_strength // 50
        defeated = min(defenders, self.devoured_in_shelter)
        self.devoured_in_shelter -= defeated
        if self.devoured_in_shelter:
            for civilian in self.shelter.civilians:
                if civilian.health > 0:
                    civilian.health = max(0, civilian.health - 25)
                    if self.devoured_in_shelter == 0:
                        break
        return self.devoured_in_shelter == 0

    def reclaim(self, territory: Territory) -> bool:
        """Reclaim a territory when the shelter has enough trained fighters."""
        if territory.reclaimed:
            return True
        strength = self.shelter.fighting_strength // 50
        if strength < territory.devoured:
            return False
        territory.reclaimed = True
        return True
