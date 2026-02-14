import os
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from soft_solar_router.persistence.file import FilePersistence

@pytest.fixture
def persistence_file(tmp_path):
    return str(tmp_path / "persistence.txt")

def test_initial_state(persistence_file):
    p = FilePersistence(persistence_file)
    now = datetime.now()
    assert not p.is_waterheater_on_manually_requested_today(now)

def test_request_manual_on(persistence_file):
    p = FilePersistence(persistence_file)
    now = datetime.now()
    p.request_manual_waterheater_on_today(now)
    assert p.is_waterheater_on_manually_requested_today(now)

def test_persistence_across_instances(persistence_file):
    p1 = FilePersistence(persistence_file)
    now = datetime.now()
    p1.request_manual_waterheater_on_today(now)
    
    p2 = FilePersistence(persistence_file)
    assert p2.is_waterheater_on_manually_requested_today(now)

@freeze_time("2023-10-27 10:00:00")
def test_day_change_logic(persistence_file):
    p = FilePersistence(persistence_file)
    now = datetime.now()
    
    # Request on "today" (Oct 27)
    p.request_manual_waterheater_on_today(now)
    assert p.is_waterheater_on_manually_requested_today(now)
    
    # Move to tomorrow 5am (still considered "today" by logic)
    with freeze_time("2023-10-28 05:00:00"):
        now = datetime.now()
        assert p.is_waterheater_on_manually_requested_today(now)

    # Move to tomorrow 7am (now considered "tomorrow")
    with freeze_time("2023-10-28 07:00:00"):
        now = datetime.now()
        assert not p.is_waterheater_on_manually_requested_today(now)

