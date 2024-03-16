from soft_solar_router.application.test.power_testable import PowerTestable
from soft_solar_router.application.test.battery_testable import BatteryTestable

from soft_solar_router.application.interfaces.power import PowerUnit
from soft_solar_router.application.utils import (
    merge_consumptions,
    extract_solar_prod,
    home_consumptions,
)
from datetime import datetime, time, timedelta

now = datetime.now()
duration = time(minute=1)
dduration = timedelta(minutes=1)


def test_merge_consumptions():

    power = PowerTestable.GenerateNet(PowerUnit.FromWatts(999), now, duration)
    battery = BatteryTestable.GenerateNet(PowerUnit.FromWatts(-999), now, duration)
    merged = merge_consumptions(now, power, battery)

    print(merged)
    assert merged.threshold(1995).distribution(normalized=True)[True] == 1
    assert merged.threshold(2000).distribution(normalized=True)[True] == 0
    time_window = merged.last_key() - merged.first_key()
    assert time_window == timedelta(seconds=66)  # should be 60 but 66 is ok_ish


def test_extract_solar_prod():

    power = PowerTestable.GenerateNet(PowerUnit.FromWatts(999), now, duration)

    solar = extract_solar_prod(now, power)

    assert solar.n_measurements() == len(power.get(now))


def test_home_consumption():
    """all solar production is used fro battery charging,
    so home load is null"""

    power = PowerTestable.GenerateProdAndNet(
        prod=PowerUnit.FromWatts(999),
        net=PowerUnit.FromWatts(0),
        now=now,
        duration=dduration,
    )
    battery = BatteryTestable.GenerateNet(PowerUnit.FromWatts(-999), now, duration)

    home = home_consumptions(now=now, power=power, battery=battery)

    assert home.distribution().min(include_zero=True) == 0
    assert home.distribution().max() == 3
