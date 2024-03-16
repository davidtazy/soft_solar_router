from typing import List
from soft_solar_router.application.interfaces.power import (
    Power,
    PowerData,
    PowerUnit,
    EnergyUnit,
)

from datetime import datetime, timedelta, time


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
                    imported_from_grid=PowerUnit.FromWatts(net.ToWatts() + (i % 2)),
                    instant_solar_production=prod,
                    total_solar_production=EnergyUnit.FromWattHours(0),
                )
            )

        return PowerTestable(ret)

    def get(self, now: datetime) -> List[PowerData]:
        return self.power

    def update(self) -> None:
        pass
