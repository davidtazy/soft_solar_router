from datetime import datetime
from soft_solar_router.application.interfaces.monitoring import MonitorData
from soft_solar_router.application.interfaces.power import EnergyUnit, PowerUnit


def test_monitor_data_to_dict():
    now = datetime(year=2020, month=12, day=25, hour=11, minute=45, second=59)
    m = MonitorData(now)

    ret = m.to_dict()
    assert ret["timestamp"] == 1608893159
    assert len(ret) == 1

    assert m.is_empty() is True

    m.power_import = PowerUnit.FromWatts(123.4)
    m.total_solar_production = EnergyUnit.FromWattHours(234.5)

    m.switch_state = True

    assert m.is_empty() is False

    ret = m.to_dict()
    print(ret)
    assert ret["power_import_watt"] == 123
    assert ret["total_solar_production_wh"] == 234
    assert ret["switch_state"] is True
