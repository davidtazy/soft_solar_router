from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
import datetime


@dataclass
class WeatherData:
    timestamp: datetime.datetime
    solar_irradiance_wm2: int


class Weather(ABC):
    @abstractmethod
    def forecast(self) -> List[WeatherData]:
        pass
