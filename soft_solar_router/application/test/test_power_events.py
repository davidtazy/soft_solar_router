from typing import List
from datetime import datetime, time, timedelta
import traces
from application.interfaces.settings import Settings
from application.interfaces.power import (
    PowerUnit,
)

from application.events import (
    is_too_much_import,
    is_no_importing,
    is_enough_sun,
    not_enought_consumption_when_switch_on,
    switch_on_since,
)
from soft_solar_router.application.interfaces.switch import SwitchHistory
from soft_solar_router.application.test.power_testable import PowerTestable


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
    dduration = timedelta(minutes=1)
    begin = now - dduration
    settings = Settings(too_much_import_duration=duration, too_much_import_watts=1000)

    not_too_much = traces.TimeSeries(
        data={
            begin: 999,
            now: 999,
        },
        default=0,
    )
    too_much = traces.TimeSeries(
        data={
            begin: 1001,
            now: 1001,
        },
        default=0,
    )
    empty = traces.TimeSeries()

    assert is_too_much_import(now, not_too_much, settings) is False
    assert is_too_much_import(now, too_much, settings) is True

    # not enough data ==> no too much import
    assert is_too_much_import(now, empty, settings) is False

    too_much_but_not_enough_data = not_too_much.slice(
        start=now - dduration / 2, end=now
    )
    assert is_too_much_import(now, too_much_but_not_enough_data, settings) is False


def test_no_power_import():
    now = datetime.now()
    duration = time(minute=1)
    dduration = timedelta(minutes=1)
    begin = now - dduration
    settings = Settings(no_import_duration=duration, no_import_watts=300)

    no_importing = traces.TimeSeries(
        data={
            begin: 299,
            now: 299,
        },
        default=0,
    )
    importing = traces.TimeSeries(
        data={
            begin: 301,
            now: 301,
        },
        default=0,
    )
    empty = traces.TimeSeries()

    assert is_no_importing(now, no_importing, settings) is True
    assert is_no_importing(now, importing, settings) is False

    # not enough data ==> no no-importing
    assert is_no_importing(now, empty, settings) is False

    no_importing_but_not_enough_data = no_importing.slice(
        start=now - dduration / 2, end=now
    )
    assert is_no_importing(now, no_importing_but_not_enough_data, settings) is False


def test_is_enough_sun():
    now = datetime.now()
    duration = time(minute=1)
    dduration = timedelta(minutes=1)
    begin = now - dduration
    settings = Settings(
        is_enough_sun_duration=duration, is_enough_sun_minimal_watts=1000
    )

    not_enough_sun = traces.TimeSeries(
        data={
            begin: 999,
            now: 999,
        },
        default=0,
    )
    enough_sun = traces.TimeSeries(
        data={
            begin: 1001,
            now: 1001,
        },
        default=0,
    )
    empty = traces.TimeSeries()

    assert is_enough_sun(now, not_enough_sun, settings) is False
    assert is_enough_sun(now, enough_sun, settings) is True

    # not enough data ==> no no-importing
    assert is_enough_sun(now, empty, settings) is False

    enough_sun_but_not_enough_data = enough_sun.slice(
        start=now - dduration / 2, end=now
    )
    assert is_enough_sun(now, enough_sun_but_not_enough_data, settings) is False


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


def test_no_enough_consumption_when_switch_on():
    now = datetime.now()
    duration = timedelta(minutes=1)
    begin = now - duration
    settings = Settings(
        no_production_when_switch_on=duration, water_heater_consumption_watts=2000
    )

    home_consumption = traces.TimeSeries(
        data={
            begin: 1499,
            now: 1499,
        },
        default=0,
    )

    switch_on = generate_switch_state(
        state=True, now=now, duration=timedelta(minutes=3), count=10
    )

    assert not_enought_consumption_when_switch_on(
        now, home_consumption, switch_on, settings
    )

    switch_off = generate_switch_state(
        state=False, now=now, duration=timedelta(minutes=3), count=10
    )

    assert (
        not_enought_consumption_when_switch_on(
            now, home_consumption, switch_off, settings
        )
        is False
    )

    home_consumption = traces.TimeSeries(
        data={
            begin: 1501,
            now: 1501,
        },
        default=0,
    )
    assert (
        not_enought_consumption_when_switch_on(
            now, home_consumption, switch_on, settings
        )
        is False
    )
