from soft_solar_router.application.interfaces.monitoring import MonitorData, Monitoring


class Fake(Monitoring):
    def push(self, measure: MonitorData) -> int:
        return -1
