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
        return self._get_duration(self._solar_heater_powered_on_duration())

    def get_solar_heater_powered_on_duration_last_night(self) -> datetime.timedelta:
        return self._get_duration(self._solar_heater_powered_on_duration_night())

    def get_solar_heater_powered_on_duration_today(self) -> datetime.timedelta:
        return self._get_duration(self._solar_heater_powered_on_duration_day())

    def _get_duration(self, query: str) -> datetime.timedelta:
        # Execute the query
        result = self.query_api.query(query)

        # Extract the result
        if result:
            for table in result:
                for record in table.records:
                    if record:
                        return datetime.timedelta(hours=record.get_value())

        logger.error(" _get_duration - No data found.")
        return datetime.timedelta()

    @staticmethod
    def _solar_heater_powered_on_duration():
        return f"""
        import "date"
        import "timezone"
        option location = timezone.location(name: "Europe/Paris")
        startTime = date.add(d: -2h, to: date.truncate(t: now(), unit: 1d))

       from(bucket: "teleinfo")
            |> range(start: startTime)
            |> filter(fn: (r) => r._measurement == "switch_state")
            |> toInt() // Assure que la valeur est 0 ou 1
            |> aggregateWindow(
                every: 24h,
                fn: (column, tables=<-) => tables |> integral(unit: 1h, column: column),
                offset: -12h
            )
            |> yield(name: "count")
        """

    @staticmethod
    def _solar_heater_powered_on_duration_night():
        return f"""
        import "date"
        import "timezone"
        option location = timezone.location(name: "Europe/Paris")
        startTime = date.add(d: -2h, to: date.truncate(t: now(), unit: 1d))
        endTime = date.add(d: 8h, to: startTime)
       from(bucket: "teleinfo")
            |> range(start: startTime, stop: endTime)
            |> filter(fn: (r) => r._measurement == "switch_state")
            |> toInt() // Assure que la valeur est 0 ou 1
            |> aggregateWindow(
                every: 24h,
                fn: (column, tables=<-) => tables |> integral(unit: 1h, column: column),
                offset: -12h
            )
            |> yield(name: "count")
        """

    @staticmethod
    def _solar_heater_powered_on_duration_day():
        return f"""
        import "date"
        import "timezone"
        option location = timezone.location(name: "Europe/Paris")
        // Point de référence : Aujourd'hui à 00:00
        today = date.truncate(t: now(), unit: 1d)

        // Start : Aujourd'hui à 6h00
        startTime = date.add(d: 6h, to: today)

        // End : Aujourd'hui à 20h00
        endTime = date.add(d: 20h, to: today)
       from(bucket: "teleinfo")
            |> range(start: startTime, stop: endTime)
            |> filter(fn: (r) => r._measurement == "switch_state")
            |> toInt() // Assure que la valeur est 0 ou 1
            |> aggregateWindow(
                every: 24h,
                fn: (column, tables=<-) => tables |> integral(unit: 1h, column: column),
                offset: -12h
            )
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
