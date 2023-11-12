from soft_solar_router.application.interfaces.switch import Switch


class SonOff(Switch):
    def set(self, state: bool) -> None:
        pass
