from soft_solar_router.grid.influx import Influx
from datetime import datetime
import logging
import os
import sys

from influxdb_client import InfluxDBClient

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)
load_dotenv()

# Define your InfluxDB connection parameters
token = os.environ.get("INFLUXDB_TOKEN")
url = os.environ.get("INFLUXDB_URL")
org = os.environ.get("INFLUXDB_ORG")

if not token:
    logging.error("env values token not set")
    sys.exit(1)
if not url:
    logging.error("env values url not set")
    sys.exit(1)
if not org:
    logging.error("env values org not set")
    sys.exit(1)

client = Influx(url, org, token)

now = datetime.now()

print(f"demain is {client._get_demain()}")
print(f"is_red_today:{client.is_red_today(now)}")
print(f"is_red_tomorrow:{client.is_red_tomorrow(now)}")
