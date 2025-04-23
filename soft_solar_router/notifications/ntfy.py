from soft_solar_router.application.interfaces.notifications import (
    Notifications,
    Notifier,
)
import datetime
import requests
import logging
import humanize

logger = logging.getLogger("nty")

NTFY_TOPIC_NAME = "tazy_soft_solar_router"
NTFY_TOPIC_ERROR_NAME = "tazy_soft_solar_router_error"


class Ntfy(Notifications):
    full_ntf = Notifier()
    start_sunny_ntf = Notifier()
    start_forced_ntf = Notifier()
    stop_sunny_ntf = Notifier()

    def notify(self, msg: str):
        self._notify(msg, NTFY_TOPIC_NAME)

    def notify_error(self, msg: str):
        self._notify(msg, NTFY_TOPIC_ERROR_NAME)

    def _notify(self, msg: str, topic: str):
        try:
            requests.post(
                f"https://ntfy.sh/{topic}",
                data=msg.encode(encoding="utf-8"),
            )
        except Exception as e:
            logger.exception(e)

    def on_full_water_heater(self, now: datetime.datetime) -> None:
        if self.full_ntf.load_and_check_if_first(now):
            self.notify("Le chauffe eau est plein !!!\n tu peux faire des machines")

    def on_start_sunny(self, now: datetime.datetime) -> None:
        if self.start_sunny_ntf.load_and_check_if_first(now):
            self.notify("Demarrage du chauffe eau par les panneaux solaires")

    def on_stop_sunny(self, now: datetime.datetime, solar_heater_powered_on_duration: datetime.timedelta) -> None:
        if self.full_ntf.is_notified_today(now):
            # dont notify because already done by the full event
            return
        if not self.start_sunny_ntf.is_notified_today(now):
            # dont notify because sunny not started today yet
            return
        if self.stop_sunny_ntf.load_and_check_if_first(now):
            self.notify(
                "Fin de chauffe eau par le solaire.\n"
                f"Durée de chauffe: {humanize.naturaldelta(solar_heater_powered_on_duration)} .\n"
                "ATTENTION le ballon d'eau chaude n'est pas plein !!! "
            )
        pass

    def on_start_forced(self, now: datetime.datetime) -> None:
        if self.start_forced_ntf.load_and_check_if_first(now):
            self.notify(
                "Demarrage du chauffe eau par edf. \ncar demain jour ROUGE ou nuageux"
            )

    def on_fatal_error(self, now: datetime.datetime, message: str) -> None:
        self.notify_error(f"Fatal Error: {message}")
