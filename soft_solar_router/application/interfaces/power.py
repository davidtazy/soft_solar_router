from abc import ABC, abstractmethod
from datetime import datetime, time
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PowerUnit:
    watts: int

    @staticmethod
    def FromWatts(watts: int):
        return PowerUnit(watts)

    @staticmethod
    def FromKiloWatts(kilo_watts: float):
        return PowerUnit(kilo_watts * 1000)

    def ToKiloWatts(self):
        return self.watts / 1000.0

    def ToWatts(self):
        return self.watts


@dataclass
class PowerData:
    timestamp: datetime
    imported_from_grid: PowerUnit


class Power(ABC):
    @abstractmethod
    def get(self, now: datetime, duration: time) -> List[PowerData]:
        """get the n last values from now - duration"""
        pass

    @abstractmethod
    def update(self) -> None:
        pass
