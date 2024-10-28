import logging
from datetime import timedelta, datetime
import time
import sys

from soft_solar_router.switch.shelly1pro import Shelly1Pro

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)


def exit_cmdline_error():
    print("please shoose --on or --off argument")
    sys.exit(1)


if len(sys.argv) < 2:
    exit_cmdline_error()

cmd = sys.argv[1]


ip = "192.168.1.37"
id = "0"
delta = timedelta(minutes=1)
switch = Shelly1Pro(delta, ip, id)


if cmd == "--on":
    logging.debug("switch on")
    switch.set(datetime.now(), True)
    logging.debug("done")

elif cmd == "--off":
    logging.debug("switch off")
    switch.set(datetime.now(), False)
    switch.set(datetime.now(), False)
    logging.debug("done")

else:
    exit_cmdline_error()
