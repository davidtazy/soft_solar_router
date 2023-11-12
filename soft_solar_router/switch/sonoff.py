import logging

from soft_solar_router.application.interfaces.switch import Switch

logger = logging.getLogger("sonoff")


class SonOff(Switch):
    state = True

    def set(self, state: bool) -> None:
        if state != self.state:
            logger.info(f"set switch state to {state}")
            self.state = state
