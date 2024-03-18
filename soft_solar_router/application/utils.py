from soft_solar_router.application.interfaces.battery import Battery
from soft_solar_router.application.interfaces.power import Power


from datetime import datetime
import traces


def merge_consumptions(now: datetime, power: Power, battery: Battery):

    grid_import_serie = traces.TimeSeries(default=0)
    for sample in power.get(now=now):
        grid_import_serie[sample.timestamp] = sample.imported_from_grid.ToWatts()

    battery_export_serie = traces.TimeSeries(default=0)
    for sample in battery.get(now=now):
        battery_power_watts = sample.instant_power.ToWatts()
        # sample.state == "Charging"
        if battery_power_watts > 0:
            battery_power_watts = 0
        # sample.state == "Discharging"
        if battery_power_watts < 0:
            battery_power_watts = -battery_power_watts

        battery_export_serie[sample.timestamp] = battery_power_watts

    trace_list = [grid_import_serie, battery_export_serie]
    merged = traces.TimeSeries.merge(trace_list, operation=sum)

    return merged


def home_consumptions(now: datetime, power: Power, battery: Battery):
    """calculate the home loads consumption."""

    grid_import_serie = traces.TimeSeries(default=0)
    solar_prod_serie = traces.TimeSeries(default=0)
    for sample in power.get(now=now):
        grid_import_serie[sample.timestamp] = sample.imported_from_grid.ToWatts()
        solar_prod_serie[sample.timestamp] = sample.instant_solar_production.ToWatts()

    battery_export_serie = traces.TimeSeries(default=0)
    for sample in battery.get(now=now):
        battery_power_watts = sample.instant_power.ToWatts()
        battery_export_serie[sample.timestamp] = -battery_power_watts

    trace_list = [grid_import_serie, battery_export_serie, solar_prod_serie]
    merged = traces.TimeSeries.merge(trace_list, operation=sum)

    return merged


def extract_solar_prod(now: datetime, power: Power):
    solar_prod_watts = traces.TimeSeries(default=0)
    for sample in power.get(now=now):
        solar_prod_watts[sample.timestamp] = sample.instant_solar_production.ToWatts()

    return solar_prod_watts
