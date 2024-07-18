import logging
import os
from datetime import time, datetime
from time import sleep
from soft_solar_router.power.envoy import Envoy
from dotenv import load_dotenv
import sys

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)

logging.info("----- Start application -----")

power = Envoy(
    host="envoy",
    token=os.getenv("ENVOY_TOKEN"),
    max_duration=time(second=30),
)


now = datetime.now()

response = power.request_test()

print(response)


sys.exit(0)


sample = power.update(now)
serie = power.get(now)

logging.info(sample)
logging.info(len(serie))
sleep(3)
