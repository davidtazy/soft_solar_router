from typing import List
from datetime import datetime, time, timedelta
from application.interfaces.settings import Settings
from application.interfaces.power import Power, PowerData, PowerUnit

from application.events import is_too_much_import, is_no_importing


class PowerTestable(Power):
    def __init__(self, value: PowerUnit, now: datetime, duration: time):
        ret = []
        delta = (
            timedelta(
                hours=duration.hour, minutes=duration.minute, seconds=duration.second
            )
            / 10
        )
        for i in reversed(range(10)):
            ret.append(
                PowerData(
                    timestamp=now - i * delta,
                    imported_from_grid=value,
                )
            )

        self.power = ret

    def get(self, now: datetime, duration: time) -> List[PowerData]:
        return self.power

    def update() -> None:
        pass


def test_too_much_power_import():
    now = datetime.now()
    duration = time(minute=1)
    settings = Settings(too_much_import_duration=duration, too_much_import_watts=1000)

    not_too_much = PowerTestable(PowerUnit.FromWatts(999), now, duration)
    too_much = PowerTestable(PowerUnit.FromWatts(1001), now, duration)

    assert False == is_too_much_import(now, not_too_much, settings)
    assert True == is_too_much_import(now, too_much, settings)


def test_no_power_import():
    now = datetime.now()
    duration = time(minute=1)
    settings = Settings(no_import_duration=duration, no_import_watts=300)

    no_importing = PowerTestable(PowerUnit.FromWatts(299), now, duration)
    importing = PowerTestable(PowerUnit.FromWatts(301), now, duration)

    assert True == is_no_importing(now, no_importing, settings)
    assert False == is_no_importing(now, importing, settings)
