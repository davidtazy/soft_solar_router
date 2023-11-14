from soft_solar_router.weather.open_meteo import OpenMeteo
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s  %(message)s",
)

weather = OpenMeteo()

weather.forecast()
