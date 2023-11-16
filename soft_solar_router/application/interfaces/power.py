from abc import ABC, abstractmethod
from datetime import datetime, time
from dataclasses import dataclass
from typing import List, Union


@dataclass(frozen=True)
class PowerUnit:
    watts: int

    @staticmethod
    def FromWatts(watts: Union[float, int]):
        return PowerUnit(int(watts))

    @staticmethod
    def FromKiloWatts(kilo_watts: float):
        return PowerUnit(int(kilo_watts * 1000))

    def ToKiloWatts(self):
        return self.watts / 1000.0

    def ToWatts(self):
        return self.watts


@dataclass(frozen=True)
class EnergyUnit:
    watt_hours: int

    @staticmethod
    def FromWattHours(watts: Union[float, int]):
        return EnergyUnit(int(watts))

    @staticmethod
    def FromKiloWattHours(kilo_watts: float):
        return EnergyUnit(int(kilo_watts * 1000))

    def ToKiloWattHours(self):
        return self.watt_hours / 1000.0

    def ToWattsHours(self):
        return self.watt_hours


@dataclass
class PowerData:
    timestamp: datetime
    imported_from_grid: PowerUnit
    instant_solar_production: PowerUnit
    total_solar_production: EnergyUnit


class Power(ABC):
    @abstractmethod
    def get(self, now: datetime, duration: time) -> List[PowerData]:
        """get the n last values from now - duration"""
        pass

    @abstractmethod
    def update(self, now: datetime) -> PowerData:
        pass
