import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

from soft_solar_router.monitoring.influx import Influx
from soft_solar_router.application.interfaces.monitoring import MonitorData, PowerUnit

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)

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


influx = Influx(url, org, token)
now = datetime.now()
m = MonitorData(now)
m.power_import = PowerUnit.FromWatts(123)
m.switch_state = True

assert influx.push(m) == 2
