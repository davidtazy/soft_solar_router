from abc import ABC, abstractmethod
from datetime import datetime

class Persistence(ABC):
    @abstractmethod
    def is_waterheater_on_manually_requested_today(self, now: datetime) -> bool:
        pass

    @abstractmethod
    def request_manual_waterheater_on_today(self, now: datetime):
        pass
