from typing import List
from datetime import datetime, time, timedelta
from application.interfaces.settings import Settings
from application.interfaces.power import (
    EnergyUnit,
    Power,
    PowerData,
    PowerUnit,
)

from application.events import (
    is_too_much_import,
    is_no_importing,
    not_enough_production_when_switch_on,
)
from soft_solar_router.application.interfaces.switch import SwitchHistory


class PowerTestable(Power):
    def __init__(self, power: List[PowerData]) -> None:
        self.power = power

    @classmethod
    def GenerateNet(cls, value: PowerUnit, now: datetime, duration: time):
        delta = timedelta(
            hours=duration.hour, minutes=duration.minute, seconds=duration.second
        )
        return cls.GenerateProdAndNet(
            prod=PowerUnit.FromWatts(0), net=value, now=now, duration=delta
        )

    @staticmethod
    def GenerateProdAndNet(
        prod: PowerUnit, net: PowerUnit, now: datetime, duration: timedelta
    ):
        ret = []
        delta = duration / 10
        for i in reversed(range(12)):
            ret.append(
                PowerData(
                    timestamp=now - i * delta,
                    imported_from_grid=net,
                    instant_solar_production=prod,
                    total_solar_production=EnergyUnit.FromWattHours(0),
                )
            )

        return PowerTestable(ret)

    def get(self, now: datetime, duration: time) -> List[PowerData]:
        return self.power

    def update(self) -> None:
        pass


def generate_switch_state(
    state: bool, now: datetime, duration: timedelta, count: int
) -> List[SwitchHistory]:
    delta = duration / count
    ret = []

    for i in reversed(range(12)):
        ret.append(
            SwitchHistory(
                timestamp=now - i * delta,
                state=state,
            )
        )
    return ret


def test_too_much_power_import():
    now = datetime.now()
    duration = time(minute=1)
    settings = Settings(too_much_import_duration=duration, too_much_import_watts=1000)

    not_too_much = PowerTestable.GenerateNet(PowerUnit.FromWatts(999), now, duration)
    too_much = PowerTestable.GenerateNet(PowerUnit.FromWatts(1001), now, duration)

    assert False == is_too_much_import(now, not_too_much, settings)
    assert True == is_too_much_import(now, too_much, settings)

    # not enough data ==> no too much import
    assert False == is_too_much_import(now, PowerTestable([]), settings)

    too_much_but_not_enough_data = PowerTestable.GenerateNet(
        PowerUnit.FromWatts(1001), now, time(second=30)
    )
    assert False == is_too_much_import(now, too_much_but_not_enough_data, settings)


def test_no_power_import():
    now = datetime.now()
    duration = time(minute=1)
    settings = Settings(no_import_duration=duration, no_import_watts=300)

    no_importing = PowerTestable.GenerateNet(PowerUnit.FromWatts(299), now, duration)
    importing = PowerTestable.GenerateNet(PowerUnit.FromWatts(301), now, duration)

    assert True == is_no_importing(now, no_importing, settings)
    assert False == is_no_importing(now, importing, settings)

    # not enough data ==> no no-importing
    assert False == is_no_importing(now, PowerTestable([]), settings)

    no_importing_but_not_enough_data = PowerTestable.GenerateNet(
        PowerUnit.FromWatts(1001), now, time(second=30)
    )
    assert False == is_no_importing(now, no_importing_but_not_enough_data, settings)


def test_no_production_when_switch_on():
    now = datetime.now()
    duration = timedelta(minutes=1)
    settings = Settings(
        no_production_when_switch_on=duration, water_heater_consumption_watts=2000
    )

    power = PowerTestable.GenerateProdAndNet(
        prod=PowerUnit.FromWatts(1000),
        net=PowerUnit.FromWatts(400),
        now=now,
        duration=duration,
    )

    switch_on = generate_switch_state(
        state=True, now=now, duration=timedelta(minutes=3), count=10
    )

    assert not_enough_production_when_switch_on(now, power, switch_on, settings)

    switch_off = generate_switch_state(
        state=False, now=now, duration=timedelta(minutes=3), count=10
    )

    assert (
        not_enough_production_when_switch_on(now, power, switch_off, settings) is False
    )
