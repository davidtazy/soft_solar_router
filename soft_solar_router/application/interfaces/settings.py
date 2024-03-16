from dataclasses import dataclass
from datetime import time, timedelta

from typing import Optional


@dataclass
class Settings:
    minimal_solar_irradiance_wm2: int = 0
    solar_time_begin: Optional[time] = None
    solar_time_end: Optional[time] = None
    forced_hour_begin: int = 0
    forced_hour_duration: int = 0
    minimal_daily_solar_hours: int = 0
    too_much_import_duration: time = time(minute=0)
    too_much_import_watts: int = 0
    no_import_duration: time = time(minute=0)
    no_import_watts: int = 0
    no_production_when_switch_on: timedelta = timedelta(minutes=0)
    water_heater_consumption_watts: int = 0

    is_enough_sun_duration: time = time(minute=0)
    is_enough_sun_minimal_watts: int = 0
