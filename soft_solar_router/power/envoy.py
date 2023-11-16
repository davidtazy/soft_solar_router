from datetime import datetime, time, timedelta
from typing import List, Tuple
import logging
import cachetools.func
import requests

from soft_solar_router.application.interfaces.power import (
    EnergyUnit,
    Power,
    PowerData,
    PowerUnit,
)

logger = logging.getLogger("envoy")


class Envoy(Power):
    def __init__(self, host, token, max_duration: time) -> None:
        self.host = host
        self.token = token
        self.duration = timedelta(
            hours=max_duration.hour,
            minutes=max_duration.minute,
            seconds=max_duration.second,
        )
        self.serie = []

    def get(self, now: datetime, duration: time) -> List[PowerData]:
        self.constraint_serie(now)
        return self.serie

    def update(self, now: datetime) -> PowerData:
        import_from_grid, solar_production = self.instant_measures()
        total_solar_production = self.total_solar_production()

        sample = PowerData(
            timestamp=now,
            imported_from_grid=import_from_grid,
            instant_solar_production=solar_production,
            total_solar_production=total_solar_production,
        )
        self.serie.append(sample)

        self.constraint_serie(now)
        return sample

    def instant_measures(self) -> Tuple[PowerUnit, PowerUnit]:
        url = f"https://{self.host}/ivp/meters/readings"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers, verify=False, timeout=5)
        response.raise_for_status()
        response = response.json()

        production = PowerUnit.FromWatts(response[0]["activePower"])
        net = PowerUnit.FromWatts(response[1]["activePower"])
        # consumption_wh = production_wh + net_wh
        # reading_time = response[0]["timestamp"]
        # timestamp = datetime.fromtimestamp(reading_time)

        return net, production

    @cachetools.func.ttl_cache(maxsize=1, ttl=30)
    def total_solar_production(self) -> EnergyUnit:
        url = f"https://{self.host}/api/v1/production"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response = response.json()
        return EnergyUnit.FromWattHours(response["wattHoursToday"])

    def constraint_serie(self, now: datetime):
        def fresh_data(sample: PowerData):
            return sample.timestamp > now - self.duration

        self.serie = list(filter(fresh_data, self.serie))
