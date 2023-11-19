from application.events import (
    is_sunny_now,
    is_forced_period_window,
    get_tomorrow_date,
    is_cloudy_tomorrow,
)
from application.interfaces.weather import Weather, WeatherData
from application.interfaces.settings import Settings
from datetime import datetime, timedelta, time
from typing import List
import pytest


class WeatherTestable(Weather):
    @classmethod
    def FromConstantValues(cls, now: datetime, constant_val):
        ret = []
        for i in range(-5, 5):
            if i != 0:
                ret.append(WeatherData(now + i * timedelta(hours=1), constant_val))

        return cls(ret)

    @classmethod
    def FromValues(cls, now: datetime, values: List[int]):
        ret = []
        for i, value in enumerate(values):
            if i != 0:
                ret.append(WeatherData(now + i * timedelta(hours=1), value))

        return cls(ret)

    def __init__(self, datas: List[WeatherData]):
        self._datas = datas

    def forecast(self) -> List[WeatherData]:
        return self._datas


def test_start_sunny_when_solar_irradiance_greater_then_value_and_during_sunny_window():
    now = datetime(2022, 10, 10, hour=13, minute=0, second=0)
    weather = WeatherTestable.FromConstantValues(now, 1000)
    settings = Settings(
        minimal_solar_irradiance_wm2=600,
        solar_time_begin=time(hour=11, minute=30),
        solar_time_end=time(hour=16, minute=0),
    )
    now = datetime(2022, 10, 10, hour=10, minute=50, second=0)
    assert is_sunny_now(weather, now, settings) is False

    now = datetime(2022, 10, 10, hour=13, minute=20, second=0)
    assert is_sunny_now(weather, now, settings) is True

    now = datetime(2022, 10, 10, hour=16, minute=20, second=0)
    assert is_sunny_now(weather, now, settings) is False


def test_stop_sunny_when_solar_irradiance_less_then_value():
    now = datetime.now()
    weather = WeatherTestable.FromConstantValues(now, 100)
    settings = Settings(minimal_solar_irradiance_wm2=600)

    assert is_sunny_now(weather, now, settings) == False


def test_start_sunny_raise_if_weather_for_now_is_not_found():
    now = datetime.now()
    weather = WeatherTestable.FromValues(now - timedelta(days=1), [100, 100, 100])
    settings = Settings(minimal_solar_irradiance_wm2=600)
    with pytest.raises(Exception):
        is_sunny_now(weather, now, settings)


def test_check_forced_during_setted_hours():
    settings = Settings(forced_hour_begin=22, forced_hour_duration=4)

    for hour in range(0, 2):
        now = datetime(2022, 10, 10, hour=hour, minute=0, second=0)
        assert is_forced_period_window(now, settings) == True

    for hour in range(2, 22):
        now = datetime(2022, 10, 10, hour=hour, minute=0, second=0)
        assert is_forced_period_window(now, settings) == False
    for hour in range(22, 24):
        now = datetime(2022, 10, 10, hour=hour, minute=0, second=0)
        assert is_forced_period_window(now, settings) == True


def test_get_tomorrow_date():
    settings = Settings(forced_hour_begin=22, forced_hour_duration=4)

    for hour in range(0, 2):
        now = datetime(2022, 10, 10, hour=hour, minute=0, second=0)
        assert get_tomorrow_date(now, settings) == now.date()

    for hour in range(2, 24):
        now = datetime(2022, 10, 10, hour=hour, minute=0, second=0)
        assert get_tomorrow_date(now, settings) == now.date() + timedelta(days=1)


def test_is_cloudy_tomorrow_cloudy_day():
    settings = Settings(
        forced_hour_begin=22,
        forced_hour_duration=4,
        minimal_daily_solar_hours=1,
        minimal_solar_irradiance_wm2=600,
    )
    now = datetime(2022, 10, 10, hour=12, minute=0, second=0)
    tomorrow = now + timedelta(days=1)
    weather = WeatherTestable.FromConstantValues(tomorrow, 100)

    assert is_cloudy_tomorrow(now, weather, settings) == True


def test_is_cloudy_tomorrow_when_sunny_day():
    settings = Settings(
        forced_hour_begin=22,
        forced_hour_duration=4,
        minimal_daily_solar_hours=1,
        minimal_solar_irradiance_wm2=600,
    )
    now = datetime(2022, 10, 10, hour=12, minute=0, second=0)
    tomorrow = now + timedelta(days=1)
    weather = WeatherTestable.FromConstantValues(tomorrow, 1000)

    assert is_cloudy_tomorrow(now, weather, settings) == False


def test_is_cloudy_tomorrow_when_not_enough_sunny_hours():
    settings = Settings(
        forced_hour_begin=22,
        forced_hour_duration=4,
        minimal_daily_solar_hours=5,
        minimal_solar_irradiance_wm2=600,
    )
    now = datetime(2022, 10, 10, hour=12, minute=0, second=0)
    tomorrow = now + timedelta(days=1)
    weather = WeatherTestable.FromValues(tomorrow, [100, 100, 1000, 100, 100])

    assert is_cloudy_tomorrow(now, weather, settings) is True
