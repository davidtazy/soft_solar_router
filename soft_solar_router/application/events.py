from typing import List
from datetime import datetime, timedelta, date, time
import logging
from soft_solar_router.application.interfaces.switch import SwitchHistory


from soft_solar_router.application.interfaces.weather import Weather, WeatherData
from soft_solar_router.application.interfaces.settings import Settings
from soft_solar_router.application.interfaces.power import Power, PowerData

logger = logging.getLogger("events")

import traces


def is_sunny_now(weather: Weather, now: datetime, settings: Settings) -> bool:
    """find the weather range for now and check if greater then setting"""

    if not is_sunny_period_window(now, settings):
        return False

    datas = weather.forecast()

    irradiance = 0
    found = False
    for i, data in enumerate(datas):
        if data.timestamp < now and datas[i + 1].timestamp > now:
            irradiance = data.solar_irradiance_wm2
            found = True
    if not found:
        raise ValueError(" cannot found forecast for now")

    return irradiance > settings.minimal_solar_irradiance_wm2


def is_sunny_period_window(now: datetime, settings: Settings):
    begin = settings.solar_time_begin
    end = settings.solar_time_end

    if not begin and not end:
        return True
    if begin and not end:
        return now.time() > begin
    if end and not begin:
        return now.time() < end
    if begin and end:
        return now.time() > begin and now.time() < end


def is_forced_period_window(now: datetime, settings: Settings):
    begin = settings.forced_hour_begin
    end = (begin + settings.forced_hour_duration) % 24

    if begin < end:
        return now.hour >= begin and now.hour < end
    else:
        return now.hour >= begin or now.hour < end
    
def is_low_hour_period_window(now: datetime):
    
    return now.hour >= 22 or now.hour < 6
  


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


def is_too_much_import(
    now: datetime, consumption_watts: traces.TimeSeries, settings: Settings
):
    duration = settings.too_much_import_duration
    dduration = timedelta(
        hours=duration.hour, minutes=duration.minute, seconds=duration.second
    )
    begin = now - dduration

    # check get all the values in the time window
    if consumption_watts.is_empty() or consumption_watts.first_key() > begin:
        return False

    ts = consumption_watts.slice(begin, now)

    logger.debug(f"is too much import {ts}")

    return (
        ts.threshold(settings.too_much_import_watts).distribution(normalized=True)[True]
        == 1
    )


def is_no_importing(
    now: datetime, consumption: traces.TimeSeries, settings: Settings
) -> bool:
    d = settings.no_import_duration
    dduration = timedelta(hours=d.hour, minutes=d.minute, seconds=d.second)
    begin = now - dduration

    # check get all the values in the time window
    if consumption.is_empty() or consumption.first_key() > begin:
        return False

    ts = consumption.slice(begin, now)

    logger.debug(f"is no importing {ts}")

    return (
        ts.threshold(settings.no_import_watts).distribution(normalized=True)[False] == 1
    )


def is_enough_sun(
    now: datetime, production_watts: traces.TimeSeries, settings: Settings
) -> bool:
    d = settings.is_enough_sun_duration
    dduration = timedelta(hours=d.hour, minutes=d.minute, seconds=d.second)
    begin = now - dduration

    # check get all the values in the time window
    if production_watts.is_empty() or production_watts.first_key() > begin:
        return False

    ts = production_watts.slice(begin, now)

    logger.debug(f"is enough sun {ts}")
    enough = (
        ts.threshold(settings.is_enough_sun_minimal_watts).distribution(
            normalized=True
        )[True]
        == 1
    )
    logger.info(f"is enough sun {enough}")
    return enough


def switch_on_since(
    now: datetime, switch_state_history: List[SwitchHistory], duration: timedelta
) -> bool:

    begin = now - duration

    if len(switch_state_history) == 0:
        return False

    ts = traces.TimeSeries()
    for switch_state in switch_state_history:
        ts[switch_state.timestamp] = switch_state.state

    ts = ts.slice(begin, now)

    state_is_always_on = ts.distribution(normalized=True)[True] == 1
    logger.info(f"is switch on since{state_is_always_on}")
    return state_is_always_on


def not_enought_consumption_when_switch_on(
    now: datetime,
    net_consumption: traces.TimeSeries,
    switch_state_history: List[SwitchHistory],
    settings: Settings,
) -> bool:
    if (
        switch_on_since(
            now, switch_state_history, settings.no_production_when_switch_on
        )
        is False
    ):
        return False

    consumption = settings.water_heater_consumption_watts * 0.75
    duration = settings.no_production_when_switch_on
    begin = now - duration

    if net_consumption.is_empty() or net_consumption.first_key() > begin:
        return False

    not_enough = (
        net_consumption.threshold(consumption).distribution(normalized=True)[False] == 1
    )
    logger.info(f"not_enought_consumption_when_switch_on {not_enough}")
    return not_enough

    def not_enough_cons(sample: PowerData) -> bool:
        return (
            sample.timestamp > begin
            and sample.timestamp < now
            and (
                sample.instant_solar_production.ToWatts()
                + sample.imported_from_grid.ToWatts()
            )
            > consumption
        )
