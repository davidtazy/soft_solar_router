from datetime import datetime, time, timedelta
from typing import List
import logging
import requests

from soft_solar_router.application.interfaces.power import Power, PowerData, PowerUnit

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

    def update(self, now: datetime) -> None:
        self.serie.append(self.last_sample(now))

        self.constraint_serie(now)

    def last_sample(self, now):
        try:
            url = f"https://{self.host}/ivp/meters/readings"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
            }

            response = requests.get(url, headers=headers, verify=False, timeout=5)
            response.raise_for_status()
            response = response.json()

            # production_wh = response[0]["activePower"]
            net_w = PowerUnit.FromWatts(response[1]["activePower"])
            # consumption_wh = production_wh + net_wh
            # reading_time = response[0]["timestamp"]
            # timestamp = datetime.fromtimestamp(reading_time)

            return PowerData(timestamp=now, imported_from_grid=net_w)
        except Exception as e:
            logger.exception(e)
            raise e

    def constraint_serie(self, now: datetime):
        def fresh_data(sample: PowerData):
            return sample.timestamp > now - self.duration

        self.serie = list(filter(fresh_data, self.serie))
