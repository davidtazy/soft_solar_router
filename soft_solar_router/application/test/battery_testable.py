from typing import List
from soft_solar_router.application.interfaces.battery import (
    Battery,
    BatteryData,
    PowerUnit,
)

from datetime import datetime, timedelta, time


class BatteryTestable(Battery):
    def __init__(self, power: List[BatteryData]) -> None:
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
                BatteryData(
                    timestamp=now - i * delta,
                    instant_power=PowerUnit.FromWatts(net.ToWatts() + 2 * (i % 2)),
                    soc_percent=50,
                    state="Idle",
                )
            )

        return BatteryTestable(ret)

    def get(self, now: datetime) -> List[BatteryData]:
        return self.power

    def update(self) -> None:
        pass
