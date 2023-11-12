import logging
import os
from datetime import time, datetime
from time import sleep
from soft_solar_router.power.envoy import Envoy
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)

logging.info("----- Start application -----")

power = Envoy(
    host="192.168.1.44",
    token=os.getenv("ENVOY_TOKEN"),
    max_duration=time(second=30),
)


while True:
    now = datetime.now()
    power.update(now)

    serie = power.get(now, duration=time(20))
    logging.info(f"now {now}")
    logging.info(f"old {serie[0].timestamp}")
    logging.info(f"now - old {now - serie[0].timestamp}")

    logging.info(len(serie))
    sleep(3)
