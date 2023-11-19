from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SwitchHistory:
    timestamp: datetime
    state: bool


class Switch(ABC):
    _history: List[SwitchHistory] = []

    def set(self, now: datetime, state: bool) -> None:
        self._history.append(SwitchHistory(now, state))

        self._history = list(
            filter(
                lambda sample: sample.timestamp > now - timedelta(seconds=60 * 3),
                self._history,
            )
        )

        self._set(state)

    @abstractmethod
    def _set(self, state: bool) -> None:
        pass

    def history(self, now: datetime, duration: timedelta):
        return list(
            filter(lambda sample: sample.timestamp > now - duration, self._history)
        )
