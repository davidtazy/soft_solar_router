from soft_solar_router.application.interfaces.monitoring import Monitoring, MonitorData

import logging
import influxdb_client


logger = logging.getLogger("influx")


class Influx(Monitoring):
    def __init__(self, url: str, org: str, token: str) -> None:
        self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        self.bucket = "teleinfo"
        self.write_api = self.client.write_api(
            write_options=influxdb_client.client.write_api.SYNCHRONOUS
        )

    def push(self, measures: MonitorData) -> int:
        if measures.is_empty():
            return 0
        points = create_points(measures=measures.to_dict())
        if len(points):
            self.write_api.write(bucket=self.bucket, record=points)

        return len(points)


def create_points(measures):
    points = []

    if "timestamp" not in measures:
        logger.warning("exclude measure, missing timestamp")
        return points

    timestamp = measures["timestamp"]
    del measures["timestamp"]

    for measure, value in measures.items():
        point = (
            influxdb_client.Point(measure)
            .tag("host", "raspberry")
            .tag("region", "envoy")
            .field("value", value)
            .time(timestamp, write_precision=influxdb_client.WritePrecision.S)
        )

        points.append(point)

    return points
