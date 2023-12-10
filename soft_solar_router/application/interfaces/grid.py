from abc import ABC, abstractmethod
from datetime import datetime


class Grid(ABC):
    @abstractmethod
    def is_red_today(self, now: datetime) -> bool:
        pass

    @abstractmethod
    def is_red_tomorrow(self, now: datetime) -> bool:
        pass
