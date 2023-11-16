from datetime import datetime, time, timedelta


class Poller:
    def __init__(self, now: datetime, period: time) -> None:
        self.period = timedelta(
            hours=period.hour, minutes=period.minute, seconds=period.second + 1
        )
        self.last_poll = now - self.period

    def poll(self, now: datetime):
        if now - self.last_poll > self.period:
            self.last_poll = now
            return True
        return False
