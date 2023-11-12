from datetime import datetime, time
from typing import List
from soft_solar_router.application.interfaces.power import Power, PowerData, PowerUnit


class Envoy(Power):
    def get(self, now: datetime, duration: time) -> List[PowerData]:
        return []

    def update(self) -> None:
        pass
