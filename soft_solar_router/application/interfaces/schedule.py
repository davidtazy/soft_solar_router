from abc import ABC, abstractmethod
import datetime


class Schedule(ABC):
    @abstractmethod
    def sunny_now(now: datetime.datetime) -> bool:
        """return True if sun is theorically out"""
        pass

    @abstractmethod
    def forced(now: datetime.datetime) -> bool:
        """
        return True if power should be forced on
        main reason should be that tomorrow is a cloudy day
        """
        pass
