from soft_solar_router.grid.edf import Edf
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)

edf = Edf()

now = datetime.now()  # - timedelta(days=1)

print(f" is red today {edf.is_red_today(now)}")
print(f" is red tomorrow {edf.is_red_tomorrow(now)}")
