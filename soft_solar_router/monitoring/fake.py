import logging
from soft_solar_router.application.interfaces.monitoring import MonitorData, Monitoring

logger = logging.getLogger("fake switch")


class FakeMonitoring(Monitoring):
    def push(self, measure: MonitorData) -> int:
        m = measure.to_dict()
        if not measure.is_empty():
            logger.info(f"push {len(m)} measure points")
        return len(m)
