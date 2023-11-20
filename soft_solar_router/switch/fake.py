from datetime import timedelta
import logging

from soft_solar_router.application.interfaces.switch import Switch

logger = logging.getLogger("fake switch")


class FakeSwitch(Switch):
    state = None

    def __init__(self, history_duration: timedelta):
        super().__init__(history_duration)

    def _set(self, state: bool) -> None:
        if state != self.state:
            logger.info(f"set switch state to {state}")
            self.state = state
