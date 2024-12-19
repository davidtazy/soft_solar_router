from datetime import datetime
import logging

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)
load_dotenv()

if False:
    from soft_solar_router.grid.api_couleur_tempo import ApiCouleurTempo
    client = ApiCouleurTempo()

    now = datetime.now()

    print(f"is_red_today:{client.is_red_today(now)}")
    print(f"is_red_tomorrow:{client.is_red_tomorrow(now)}")


    print(f"is_red_today:{client.is_red_today(now)}")
    print(f"is_red_tomorrow:{client.is_red_tomorrow(now)}")
else:
    import os
    import sys
    from soft_solar_router.grid.influx import Influx
        
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

    print(
        f"get_solar_heater_powered_on_duration:{influx.get_solar_heater_powered_on_duration()}" 
        )