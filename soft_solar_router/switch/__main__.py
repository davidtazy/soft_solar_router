import logging
from datetime import timedelta, datetime
import time

from soft_solar_router.switch.shelly1pro import Shelly1Pro

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)


ip = "192.168.1.43"
id = "0"
delta = timedelta(minutes=1)
switch = Shelly1Pro(delta, ip, id)

logging.debug("switch on")
switch.set(datetime.now(), True)
logging.debug("done")

time.sleep(3)

logging.debug("switch off")
switch.set(datetime.now(), False)
logging.debug("done")
