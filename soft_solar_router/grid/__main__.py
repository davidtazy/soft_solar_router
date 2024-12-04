from soft_solar_router.grid.api_couleur_tempo import ApiCouleurTempo
from datetime import datetime
import logging

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)
load_dotenv()

client = ApiCouleurTempo()

now = datetime.now()

print(f"is_red_today:{client.is_red_today(now)}")
print(f"is_red_tomorrow:{client.is_red_tomorrow(now)}")


print(f"is_red_today:{client.is_red_today(now)}")
print(f"is_red_tomorrow:{client.is_red_tomorrow(now)}")
