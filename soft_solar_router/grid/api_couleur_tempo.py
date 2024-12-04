from datetime import datetime, date, timedelta
import requests
from typing import Optional
import logging

from soft_solar_router.application.interfaces.grid import Grid

logger = logging.getLogger("api_couleur_tempo")


class ApiCouleurTempo(Grid):
    TEMPO_ROUGE = 3

    def __init__(self):
        self.cache = {}

    def is_red_today(self, now: datetime) -> Optional[bool]:
        today = now.date()
        if self.cache.get(today) is None:
            self.update(today)
        return self.cache.get(today) == self.TEMPO_ROUGE

    def is_red_tomorrow(self, now: datetime) -> Optional[bool]:
        tomorrow = self.tomorrow(now.date())
        if self.cache.get(tomorrow) is None:
            self.update(tomorrow)
        return self.cache.get(tomorrow) == self.TEMPO_ROUGE

    def update(self, now: date):
        logger.info(f"request tempo for {now}")
        today = now.strftime("%Y-%m-%d")

        r = requests.get(
            f"https://www.api-couleur-tempo.fr/api/jourTempo/{today}",
        )
        if r.status_code != 200:
            logger.error(f"failed to request tempo {r.status_code}")
            return
        ret = r.json()

        logger.info(ret)

        if ret["codeJour"] != 0:
            self.cache[now] = ret["codeJour"]

    @staticmethod
    def tomorrow(now: date):
        return now + timedelta(days=1)
