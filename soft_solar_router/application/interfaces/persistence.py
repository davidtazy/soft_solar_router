from abc import ABC, abstractmethod
from datetime import datetime

class Persistence(ABC):
    @abstractmethod
    def is_waterheater_on_manually_requested_today(self, now: datetime) -> bool:
        pass

    @abstractmethod
    def set_manual_request(self, now: datetime, enabled: bool):
        pass
