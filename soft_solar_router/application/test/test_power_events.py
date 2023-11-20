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
    switch_on_since,
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

    assert is_too_much_import(now, not_too_much, settings) is False
    assert is_too_much_import(now, too_much, settings) is True

    # not enough data ==> no too much import
    assert is_too_much_import(now, PowerTestable([]), settings) is False

    too_much_but_not_enough_data = PowerTestable.GenerateNet(
        PowerUnit.FromWatts(1001), now, time(second=30)
    )
    assert is_too_much_import(now, too_much_but_not_enough_data, settings) is False


def test_no_power_import():
    now = datetime.now()
    duration = time(minute=1)
    settings = Settings(no_import_duration=duration, no_import_watts=300)

    no_importing = PowerTestable.GenerateNet(PowerUnit.FromWatts(299), now, duration)
    importing = PowerTestable.GenerateNet(PowerUnit.FromWatts(301), now, duration)

    assert is_no_importing(now, no_importing, settings) is True
    assert is_no_importing(now, importing, settings) is True

    # not enough data ==> no no-importing
    assert is_no_importing(now, PowerTestable([]), settings) is False

    no_importing_but_not_enough_data = PowerTestable.GenerateNet(
        PowerUnit.FromWatts(1001), now, time(second=30)
    )
    assert is_no_importing(now, no_importing_but_not_enough_data, settings) is False


def test_switch_on_since_with_only_one_sample_too_recent_is_not_suffisant():
    now = datetime.now()

    assert (
        switch_on_since(now, [SwitchHistory(now, state=True)], timedelta(minutes=1))
        is False
    )
    assert (
        switch_on_since(
            now,
            [SwitchHistory(now - timedelta(seconds=30), state=True)],
            timedelta(minutes=1),
        )
        is False
    )


def test_switch_on_since_with_one_old_sample_is_ok():
    now = datetime.now()

    switch_on_once = [SwitchHistory(now - timedelta(minutes=2), state=True)]

    assert switch_on_since(now, switch_on_once, timedelta(minutes=1)) is True


def test_switch_on_with_switch_off_false():
    now = datetime.now()

    switch_on_once = [
        SwitchHistory(now - timedelta(minutes=2), state=True),
        SwitchHistory(now - timedelta(seconds=30), state=False),
        SwitchHistory(now - timedelta(seconds=1), state=True),
    ]

    assert switch_on_since(now, switch_on_once, timedelta(minutes=1)) is False


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
