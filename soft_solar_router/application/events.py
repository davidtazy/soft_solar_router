from typing import List
from datetime import datetime, timedelta, date, time
import logging
from soft_solar_router.application.interfaces.switch import SwitchHistory


from soft_solar_router.application.interfaces.weather import Weather, WeatherData
from soft_solar_router.application.interfaces.settings import Settings
from soft_solar_router.application.interfaces.power import Power, PowerData

logger = logging.getLogger("events")


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
        logger.warning(" serie is empty")
        return False

    if begin - serie[0].timestamp < timedelta(seconds=1):
        logger.warning("not enough data")
        return False

    def importing(sample: PowerData) -> bool:
        return (
            sample.timestamp > begin
            and sample.timestamp < now
            and sample.imported_from_grid.ToWatts() > settings.no_import_watts
        )

    serie = list(filter(importing, serie))

    logger.debug(f"is no importing {len(serie)} :  {serie}")

    return len(serie) == 0


def switch_on_since(
    now: datetime, switch_state_history: List[SwitchHistory], duration: timedelta
):
    if len(switch_state_history) == 0:
        return False

    if switch_state_history[-1] is False:
        return False

    begin = now - duration

    # get all elements in the time window + the first older one
    state = list(reversed(switch_state_history))
    last_index = -1
    for i, sample in enumerate(state):
        if sample.timestamp <= begin:
            last_index = i + 1
    if last_index < 0:
        return False
    state = state[0:last_index]

    if len(state) == 0:
        return False

    def switch_is_off(sample: SwitchHistory) -> bool:
        return sample.state is False

    serie = list(filter(switch_is_off, state))
    return len(serie) == 0


def not_enought_consumption_when_switch_on(
    now: datetime,
    power: Power,
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

    serie = power.get(now, time(minute=duration.microseconds))

    if len(serie) == 0:
        logger.warning(" serie is empty")
        return False

    if begin - serie[0].timestamp < timedelta(seconds=1):
        logger.warning("not enough data")
        return False

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

    serie = list(filter(not_enough_cons, serie))
    return len(serie) == 0
