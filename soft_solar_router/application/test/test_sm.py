from application.state_machine import SolarRouterStateMachine


def test_expect_switch_off_when_sm_start():
    sm = SolarRouterStateMachine()
    assert sm.expected_switch_state is False
    assert sm.idle.is_active


def test_not_transiting_events_are_ignored():
    sm = SolarRouterStateMachine()

    sm.event_no_importing()
    sm.event_too_much_import()
    sm.event_stop_forced()
    sm.event_stop_sunny()

    assert sm.idle.is_active


def test_start_then_stop_forced():
    sm = SolarRouterStateMachine()

    sm.event_start_forced()

    assert sm.expected_switch_state is True
    assert sm.forced_on.is_active

    sm.event_stop_forced()

    assert sm.expected_switch_state is False
    assert sm.idle.is_active


def test_start_sunny_on_expect_switch_on():
    sm = SolarRouterStateMachine()

    sm.event_start_sunny()

    assert sm.expected_switch_state is True
    assert sm.sunny_on.is_active


def test_sunny_on_transite_to_sunny_off_when_too_much_power_imported():
    sm = SolarRouterStateMachine()
    sm.event_start_sunny()

    sm.event_too_much_import()

    assert sm.expected_switch_state is False
    assert sm.sunny_off.is_active


def test_sunny_off_transite_to_sunny_on_when_no_importing():
    sm = SolarRouterStateMachine()
    sm.event_start_sunny()
    sm.event_too_much_import()

    sm.event_no_importing()

    assert sm.expected_switch_state is True
    assert sm.sunny_on.is_active
