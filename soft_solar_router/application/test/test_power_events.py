from typing import List
from datetime import datetime, time, timedelta
from application.interfaces.settings import Settings
from application.interfaces.power import (
    EnergyUnit,
    Power,
    PowerData,
    PowerUnit,
    EnergyUnit,
)

from application.events import is_too_much_import, is_no_importing


class PowerTestable(Power):
    def __init__(self, power: List[PowerData]) -> None:
        self.power = power

    @staticmethod
    def Generate(value: PowerUnit, now: datetime, duration: time):
        ret = []
        delta = (
            timedelta(
                hours=duration.hour, minutes=duration.minute, seconds=duration.second
            )
            / 10
        )
        for i in reversed(range(12)):
            ret.append(
                PowerData(
                    timestamp=now - i * delta,
                    imported_from_grid=value,
                    instant_solar_production=PowerUnit.FromWatts(0),
                    total_solar_production=EnergyUnit.FromWattHours(0),
                )
            )

        return PowerTestable(ret)

    def get(self, now: datetime, duration: time) -> List[PowerData]:
        return self.power

    def update() -> None:
        pass


def test_too_much_power_import():
    now = datetime.now()
    duration = time(minute=1)
    settings = Settings(too_much_import_duration=duration, too_much_import_watts=1000)

    not_too_much = PowerTestable.Generate(PowerUnit.FromWatts(999), now, duration)
    too_much = PowerTestable.Generate(PowerUnit.FromWatts(1001), now, duration)

    assert False == is_too_much_import(now, not_too_much, settings)
    assert True == is_too_much_import(now, too_much, settings)

    # not enough data ==> no too much import
    assert False == is_too_much_import(now, PowerTestable([]), settings)

    too_much_but_not_enough_data = PowerTestable.Generate(
        PowerUnit.FromWatts(1001), now, time(second=30)
    )
    assert False == is_too_much_import(now, too_much_but_not_enough_data, settings)


def test_no_power_import():
    now = datetime.now()
    duration = time(minute=1)
    settings = Settings(no_import_duration=duration, no_import_watts=300)

    no_importing = PowerTestable.Generate(PowerUnit.FromWatts(299), now, duration)
    importing = PowerTestable.Generate(PowerUnit.FromWatts(301), now, duration)

    assert True == is_no_importing(now, no_importing, settings)
    assert False == is_no_importing(now, importing, settings)

    # not enough data ==> no no-importing
    assert False == is_no_importing(now, PowerTestable([]), settings)

    no_importing_but_not_enough_data = PowerTestable.Generate(
        PowerUnit.FromWatts(1001), now, time(second=30)
    )
    assert False == is_no_importing(now, no_importing_but_not_enough_data, settings)
