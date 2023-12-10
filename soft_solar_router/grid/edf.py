from datetime import datetime, date, timedelta
import requests
from typing import Optional
import logging

from soft_solar_router.application.interfaces.grid import Grid

logger = logging.getLogger("envoy")


class Edf(Grid):
    TEMPO_ROUGE = "TEMP0_ROUGE"

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
            self.update(now.date())
        return self.cache.get(tomorrow) == self.TEMPO_ROUGE

    def update(self, now: date):
        logger.info(f"request tempo for {now}")
        today = now.strftime("%Y-%m-%d")
        r = requests.get(
            "https://particulier.edf.fr/services/rest/"
            f"referentiel/searchTempoStore?dateRelevant={today}",
        )
        if r.status_code != 200:
            logger.error(f"failed to request tempo {r.status_code}")
            return
        ret = r.json()

        if ret["couleurJourJ"] != "NON_DEFINI":
            self.cache[now] = ret["couleurJourJ"]
        tomorrow = self.tomorrow(now)
        if ret["couleurJourJ1"] != "NON_DEFINI":
            self.cache[tomorrow] = ret["couleurJourJ1"]

    @staticmethod
    def tomorrow(now: date):
        return now + timedelta(days=1)
