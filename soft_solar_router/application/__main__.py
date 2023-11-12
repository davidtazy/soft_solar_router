from datetime import datetime, time, timedelta
from time import sleep
import logging
from logging.handlers import RotatingFileHandler
import os

from dotenv import load_dotenv


from soft_solar_router.application.state_machine import (
    SolarRouterStateMachine,
    LogObserver,
)
from soft_solar_router.application.interfaces.settings import Settings
from soft_solar_router.application.events import (
    is_forced_period_window,
    is_cloudy_tomorrow,
    is_sunny_now,
    is_no_importing,
    is_too_much_import,
)
from soft_solar_router.application.interfaces.switch import Switch
from soft_solar_router.application.interfaces.power import Power
from soft_solar_router.application.interfaces.weather import Weather

from soft_solar_router.weather.open_meteo import OpenMeteo
from soft_solar_router.power.envoy import Envoy
from soft_solar_router.switch.sonoff import SonOff


load_dotenv()

logging.basicConfig(
    handlers=[
        RotatingFileHandler("soft_solar_router.log", maxBytes=10240000, backupCount=5)
    ],
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)

logging.info("----- Start application -----")


class Poller:
    def __init__(self, now: datetime, period: time) -> None:
        self.period = timedelta(
            hours=period.hour, minutes=period.minute, seconds=period.second + 1
        )
        self.last_poll = now - self.period

    def poll(self, now: datetime):
        if now - self.last_poll > self.period:
            self.last_poll = now
            return True
        return False


def main():
    settings = Settings(
        minimal_solar_irradiance_wm2=600,
        forced_hour_begin=22,
        forced_hour_duration=4,
        minimal_daily_solar_hours=4,
        too_much_import_duration=time(minute=1),
        too_much_import_watts=1000,
        no_import_duration=time(minute=5),
        no_import_watts=200,
    )

    # build
    now = datetime.now()
    sm = SolarRouterStateMachine()
    sm.add_observer(LogObserver())
    sm_poller = Poller(now, time(minute=1))
    power_poller = Poller(now, time(second=5))
    weather = OpenMeteo()  # ok
    power = Envoy(
        host="192.168.1.44",
        token=os.getenv("ENVOY_TOKEN"),
        max_duration=settings.no_import_duration,
    )  # ok
    switch = SonOff()  # todo

    # run event loop
    while True:
        now = datetime.now()
        run(settings, now, sm, sm_poller, power_poller, weather, power, switch)
        sleep(1)


def run(
    settings: Settings,
    now: datetime,
    sm: SolarRouterStateMachine,
    sm_poller: Poller,
    power_poller: Poller,
    weather: Weather,
    power: Power,
    switch: Switch,
):
    if power_poller.poll(now):
        power.update(now)

    if sm_poller.poll(now):
        logging.info("generate events")

        if is_forced_period_window(now, settings) and is_cloudy_tomorrow(
            now, weather, settings
        ):
            sm.event_start_forced()
        else:
            sm.event_stop_forced()

        if is_sunny_now(weather, now, settings):
            sm.event_start_sunny()
        else:
            sm.event_stop_sunny()

        if is_too_much_import(now, power, settings):
            logging.info("too_much_import events")
            sm.event_too_much_import()

        if is_no_importing(now, power, settings):
            logging.info("no_importing events")
            sm.event_no_importing()

        switch.set(sm.expected_switch_state)


main()
