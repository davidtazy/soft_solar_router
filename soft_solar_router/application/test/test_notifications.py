import datetime
from soft_solar_router.application.interfaces.notifications import Notifier


def test_notify_once_a_day_every_event():
    ntf = Notifier()
    now = datetime.datetime.now()
    assert ntf.is_notified_today(now) is False
    assert ntf.load_and_check_if_first(now) is True
    assert ntf.load_and_check_if_first(now) is False
    assert ntf.is_notified_today(now) is True

    now = now + datetime.timedelta(days=1)

    assert ntf.is_notified_today(now) is False
    assert ntf.load_and_check_if_first(now) is True
    assert ntf.load_and_check_if_first(now) is False
    assert ntf.is_notified_today(now) is True
