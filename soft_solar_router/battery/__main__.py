from datetime import time, datetime
from soft_solar_router.battery.victron_modbus_tcp import VictronModbusTcp
from soft_solar_router.battery.victron_modbus_tcp import BatteryData
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)

battery = VictronModbusTcp(host="192.168.1.41", max_duration=time(second=30))

data = battery.update(datetime.now())

print(data)
