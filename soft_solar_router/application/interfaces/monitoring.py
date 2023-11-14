from abc import ABC, abstractmethod
from dataclasses import dataclass, fields


from datetime import datetime
from typing import Optional

from .power import PowerUnit


@dataclass
class MonitorData:
    timestamp: datetime
    power_import: Optional[PowerUnit] = None
    switch_state: Optional[bool] = None

    def is_empty(self) -> bool:
        return len(self.to_dict()) <= 1

    def to_dict(self):
        ret = {}
        for field in fields(self):
            self._append_to_dict(ret, field)
        return ret

    def _append_to_dict(self, ret, field):
        value = getattr(self, field.name)
        name = field.name

        if value is None:
            return

        if isinstance(value, datetime):
            value = int(value.timestamp())

        if isinstance(value, PowerUnit):
            value = value.ToWatts()
            name = f"{name}_watt"

        ret[name] = value


class Monitoring(ABC):
    @abstractmethod
    def push(self, measure: MonitorData) -> int:
        pass
