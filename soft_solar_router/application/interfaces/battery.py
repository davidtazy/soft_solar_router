from abc import ABC, abstractmethod
from datetime import datetime, time, timedelta
from dataclasses import dataclass
from typing import List, Union
from .power import PowerUnit, EnergyUnit


@dataclass
class BatteryData:
    timestamp: datetime
    soc_percent: int
    instant_power: PowerUnit
    state: str


class Battery(ABC):
    @abstractmethod
    def get(self, now: datetime, duration: time) -> List[BatteryData]:
        """get the n last values from now - duration"""
        pass

    @abstractmethod
    def update(self, now: datetime) -> BatteryData:
        pass
