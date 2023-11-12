from dataclasses import dataclass
from datetime import time


@dataclass
class Settings:
    minimal_solar_irradiance_wm2: int = 0
    forced_hour_begin: int = 0
    forced_hour_duration: int = 0
    minimal_daily_solar_hours: int = 0
    too_much_import_duration: time = time(minute=0)
    too_much_import_watts: int = 0
    no_import_duration: int = time(minute=0)
    no_import_watts: int = 0
