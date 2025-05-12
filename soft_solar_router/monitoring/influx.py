import datetime
import typing
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
        self.query_api = self.client.query_api()

    def push(self, measures: MonitorData) -> int:
        if measures.is_empty():
            return 0
        points = create_points(measures=measures.to_dict())
        if len(points):
            self.write_api.write(bucket=self.bucket, record=points)

        return len(points)
    
    def get_solar_heater_powered_on_duration(self) -> datetime.timedelta:
        # Execute the query
        result = self.query_api.query(self._solar_heater_powered_on_duration())

        # Extract the result
        if result:
            for table in result:
                for record in table.records:
                    if record:
                        return datetime.timedelta(seconds=int(record.get_value()))*60
                    

        logger.error(" get_solar_heater_powered_on_duration - No data found.")
        return datetime.timedelta()

    @staticmethod
    def _solar_heater_powered_on_duration():
        return f"""
        from(bucket: "teleinfo")
            |> range(start: -12h)
            |> filter(fn: (r) => r._measurement == "switch_state")
            |> toInt()
            |> stateDuration(column: "_value", fn: (r)=> r._value == 1)
            |> aggregateWindow(every:1d,       fn: sum)
            |> yield(name: "count")
        """



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
