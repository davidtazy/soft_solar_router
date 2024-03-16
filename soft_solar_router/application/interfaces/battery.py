from abc import ABC, abstractmethod
from datetime import datetime, time
from dataclasses import dataclass
from typing import List
from .power import PowerUnit


@dataclass
class BatteryData:
    timestamp: datetime
    soc_percent: int
    instant_power: PowerUnit
    state: str


class Battery(ABC):
    @abstractmethod
    def get(self, now: datetime) -> List[BatteryData]:
        """get the n last values from now"""
        pass

    @abstractmethod
    def update(self, now: datetime) -> BatteryData:
        pass
