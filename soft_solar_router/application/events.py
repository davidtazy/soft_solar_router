from typing import List
from datetime import datetime, timedelta, date
import logging


from soft_solar_router.application.interfaces.weather import Weather, WeatherData
from soft_solar_router.application.interfaces.settings import Settings
from soft_solar_router.application.interfaces.power import Power, PowerData

logger = logging.getLogger("events")


def is_sunny_now(weather: Weather, now: datetime, settings: Settings) -> bool:
    """find the weather range for now and check if creater then value"""
    datas = weather.forecast()

    irradiance = 0
    found = False
    for i, data in enumerate(datas):
        if data.timestamp < now and datas[i + 1].timestamp > now:
            irradiance = data.solar_irradiance_wm2
            found = True
    if not found:
        logger.critical(" cannot found forecast for now")
        raise ValueError(" cannot found forecast for now")

    return irradiance > settings.minimal_solar_irradiance_wm2


def is_forced_period_window(now: datetime, settings: Settings):
    begin = settings.forced_hour_begin
    end = (begin + settings.forced_hour_duration) % 24

    if begin < end:
        return now.hour >= begin and now.hour < end
    else:
        return now.hour >= begin or now.hour < end


def get_tomorrow_date(now: datetime, settings: Settings) -> date:
    begin = settings.forced_hour_begin
    end = (begin + settings.forced_hour_duration) % 24
    if begin < end:
        tomorrow = now + timedelta(days=1)
    else:
        if now.hour < end:
            tomorrow = now
        else:
            tomorrow = now + timedelta(days=1)
    return tomorrow.date()


def is_cloudy_tomorrow(now: datetime, weather: Weather, settings: Settings):
    tomorrow = get_tomorrow_date(now, settings)

    forecast = weather.forecast()

    def tomorrow_condition(sample: WeatherData) -> bool:
        return sample.timestamp.date() == tomorrow

    forecast = list(filter(tomorrow_condition, forecast))

    if len(forecast) == 0:
        logger.critical("cannot get forecast for tomorrow")
        return False

    def sunny_condition(sample: WeatherData) -> bool:
        return sample.solar_irradiance_wm2 > settings.minimal_solar_irradiance_wm2

    forecast = list(filter(sunny_condition, forecast))

    return len(forecast) < settings.minimal_daily_solar_hours


def is_too_much_import(now: datetime, power: Power, settings: Settings) -> bool:
    d = settings.too_much_import_duration
    begin = now - timedelta(hours=d.hour, minutes=d.minute, seconds=d.second)

    serie = power.get(now, d)

    if len(serie) == 0:
        return False

    if begin - serie[0].timestamp < timedelta(seconds=1):
        return False

    def not_too_much(sample: PowerData) -> bool:
        return (
            sample.timestamp > begin
            and sample.timestamp < now
            and sample.imported_from_grid.ToWatts() < settings.too_much_import_watts
        )

    ret = list(filter(not_too_much, serie))

    return len(ret) == 0


def is_no_importing(now: datetime, power: Power, settings: Settings) -> bool:
    d = settings.no_import_duration
    begin = now - timedelta(hours=d.hour, minutes=d.minute, seconds=d.second)

    serie = power.get(now, d)

    if len(serie) == 0:
        return False

    if begin - serie[0].timestamp < timedelta(seconds=1):
        return False

    def importing(sample: PowerData) -> bool:
        return (
            sample.timestamp > begin
            and sample.timestamp < now
            and sample.imported_from_grid.ToWatts() > settings.no_import_watts
        )

    ret = list(filter(importing, power.get(now, d)))

    return len(ret) == 0
