from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from soft_solar_router.webview.router import create_router

# Mock dependencies
mock_weather = MagicMock()
mock_settings = MagicMock()
mock_monitoring = MagicMock()
mock_persistence = MagicMock()

# Setup mocks
from datetime import timedelta, datetime
mock_monitoring.get_solar_heater_powered_on_duration.return_value = timedelta(hours=2, minutes=30)
mock_monitoring.get_solar_heater_powered_on_duration_last_night.return_value = timedelta(hours=5)
mock_monitoring.get_solar_heater_powered_on_duration_today.return_value = timedelta(hours=1, minutes=30)
mock_monitoring.get_last_time_status_full.return_value = datetime.now() - timedelta(days=2)
mock_persistence.is_waterheater_on_manually_requested_today.return_value = False

# Setup Settings mock values used in events.py
mock_settings.forced_hour_begin = 22
mock_settings.forced_hour_duration = 6
mock_settings.minimal_solar_irradiance_wm2 = 200
mock_settings.minimal_daily_solar_hours = 4

# Setup Weather mock
from soft_solar_router.application.interfaces.weather import WeatherData
from datetime import datetime
mock_weather.forecast.return_value = [] # Empty forecast for now, or populate if needed by is_cloudy_tomorrow logic

# Create app with mocked dependencies
app = FastAPI()
router = create_router(mock_weather, mock_settings, mock_monitoring, mock_persistence)
app.include_router(router)

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Mon chauffe eau" in response.text
    assert "2h 30m" in response.text
    assert "☀️ Temps ensoleillé demain" in response.text
    
def test_force_on():
    response = client.post("/force", data={"force_state": "true"})
    assert response.status_code == 200
    # Verify called with True
    args, _ = mock_persistence.set_manual_request.call_args
    assert args[1] is True

def test_force_off():
    # When checkbox is unchecked, no data is sent for it. FastAPI Form(False) handles this.
    response = client.post("/force", data={}) 
    assert response.status_code == 200
    # Verify called with False
    # Get the last call arguments
    args, _ = mock_persistence.set_manual_request.call_args
    assert args[1] is False

