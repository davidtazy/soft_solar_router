from datetime import datetime, timedelta
import os
from soft_solar_router.application.interfaces.persistence import Persistence

class FilePersistence(Persistence):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._cached_date = None
        self._load()

    def _get_adjusted_today(self,now: datetime) -> str:
        # Today is defined as now - 6 hours
        adjusted_now = now - timedelta(hours=6)
        return adjusted_now.strftime("%Y-%m-%d")

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self._cached_date = f.read().strip()

    def _save(self):
        with open(self.file_path, "w") as f:
            f.write(self._cached_date)

    def is_waterheater_on_manually_requested_today(self, now: datetime) -> bool:
        return self._cached_date == self._get_adjusted_today(now)

    def set_manual_request(self, now: datetime, enabled: bool):
        if enabled:
            self._cached_date = self._get_adjusted_today(now)
        else:
            self._cached_date = ""
        self._save()
