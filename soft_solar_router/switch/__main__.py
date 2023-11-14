from soft_solar_router.switch.sonoff import SonOff
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)

load_dotenv()
ip_address = "192.168.1.50"
api_key = os.getenv("SONOFF_API_KEY")
device_id = "1000bb555e"  # not really required


switch = SonOff(ip_address=ip_address, api_key=api_key, device_id=device_id)


switch.set(False)
