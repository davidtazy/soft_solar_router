from datetime import datetime
import logging
import typing
from soft_solar_router.application.interfaces.grid import Grid
from influxdb_client import InfluxDBClient

logger = logging.getLogger(__file__)


class Influx(Grid):
    def __init__(self, url: str, org: str, token: str) -> None:
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.demain_query = self._query("DEMAIN")
        self.ptec_query = self._query("PTEC")

    def is_red_today(self, now: datetime) -> bool:
        ptec: str = self._get_ptec()
        if ptec is None:
            return False
        return ptec.endswith("JR")

    def is_red_tomorrow(self, now: datetime) -> bool:
        demain = self._get_demain()
        if demain is None:
            return False
        return demain.startswith("ROU")

    def _get_demain(self) -> typing.Optional[str]:
        # Execute the query
        query_api = self.client.query_api()
        result = query_api.query(self.demain_query)

        # Extract the result
        if result:
            for table in result:
                for record in table.records:
                    return record.get_value()

        else:
            logger.error("get demain - No data found.")
        return None

    def _get_ptec(self):
        # Execute the query
        query_api = self.client.query_api()
        result = query_api.query(self.ptec_query)

        # Extract the result
        if result:
            for table in result:
                for record in table.records:
                    return record.get_value()
        else:
            logger.error("get ptec - No data found.")
        return None

    @staticmethod
    def _query(measurement_name):
        bucket = "teleinfo"
        region = "linky"
        return f"""
            from(bucket: "{bucket}")
            |> range(start: -1h)  // Set the time range for the search (e.g., last hour)
            |> filter(fn: (r) => r._measurement == "{measurement_name}")
            |> filter(fn: (r) => r.host == "raspberry" and r.region == "{region}")
            |> sort(columns: ["_time"], desc: true)
            |> limit(n: 1)
            """
