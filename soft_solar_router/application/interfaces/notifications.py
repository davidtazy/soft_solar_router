from abc import ABC, abstractmethod
import datetime


class Notifier:
    last_notif: datetime.date = datetime.datetime.fromtimestamp(0.0).date()

    def load_and_check_if_first(self, now: datetime.datetime) -> bool:
        today = now.date()
        ln = self.last_notif
        self.last_notif = today

        return ln != today

    def is_notified_today(self, now: datetime.datetime) -> bool:
        today = now.date()
        return self.last_notif == today


class Notifications(ABC):
    @abstractmethod
    def on_full_water_heater(self, now: datetime.datetime) -> None:
        pass

    @abstractmethod
    def on_start_sunny(self, now: datetime.datetime) -> None:
        pass

    @abstractmethod
    def on_stop_sunny(self, now: datetime.datetime) -> None:
        pass

    @abstractmethod
    def on_start_forced(self, now: datetime.datetime) -> None:
        pass

    @abstractmethod
    def on_fatal_error(self, now: datetime.datetime, message: str) -> None:
        pass
