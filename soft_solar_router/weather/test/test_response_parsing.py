from datetime import datetime
from soft_solar_router.weather.open_meteo import OpenMeteo, WeatherData


def test_http_response_to_weather_data():
    ret = OpenMeteo.parse(
        [
            0.0,
            11.7,
            2.6,
        ],
        [
            "2023-10-30T00:00",
            "2023-10-30T01:00",
            "2023-10-30T02:00",
        ],
    )
    assert ret == [
        WeatherData(timestamp=datetime(2023, 10, 30, 0, 0), solar_irradiance_wm2=0.0),
        WeatherData(timestamp=datetime(2023, 10, 30, 1, 0), solar_irradiance_wm2=11.7),
        WeatherData(timestamp=datetime(2023, 10, 30, 2, 0), solar_irradiance_wm2=2.6),
    ]
