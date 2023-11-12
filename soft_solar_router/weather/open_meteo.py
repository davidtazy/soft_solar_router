from typing import List
import logging
from datetime import datetime

import requests

from soft_solar_router.application.interfaces.weather import Weather, WeatherData
import cachetools.func


logger = logging.getLogger("open-meteo")


class OpenMeteo(Weather):
    @cachetools.func.ttl_cache(maxsize=128, ttl=60 * 60)
    def forecast(self) -> List[WeatherData]:
        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast?latitude=43.351&longitude=6.122&hourly=direct_normal_irradiance_instant&timezone=auto&forecast_days=2",
                verify=False,
            )
            response.raise_for_status()
            response = response.json()
            logger.info(response["hourly"]["direct_normal_irradiance_instant"])
            logger.info(response["hourly"]["time"])
            return self.parse(
                response["hourly"]["direct_normal_irradiance_instant"],
                response["hourly"]["time"],
            )
        except Exception as e:
            logger.exception(e)
            return []

    @staticmethod
    def parse(
        hourly_irradiance: List[float], timestamps: List[str]
    ) -> List[WeatherData]:
        assert len(hourly_irradiance) == len(timestamps)
        ret = []
        for i in range(len(hourly_irradiance)):
            ret.append(
                WeatherData(
                    timestamp=datetime.fromisoformat(timestamps[i]),
                    solar_irradiance_wm2=hourly_irradiance[i],
                )
            )

        return ret
