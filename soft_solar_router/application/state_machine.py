import logging
from statemachine import StateMachine, State

logger = logging.getLogger("state machine")


class SolarRouterStateMachine(StateMachine):
    "solar router state machine"
    idle = State(initial=True)
    sunny_on = State()
    sunny_off = State()
    forced_on = State()
    full = State()
    forced_full = State()

    event_start_sunny = idle.to(sunny_on)
    event_stop_sunny = sunny_on.to(idle) | sunny_off.to(idle) | full.to(idle)
    event_too_much_import = sunny_on.to(sunny_off)
    event_no_importing = sunny_off.to(sunny_on)

    event_start_forced = idle.to(forced_on)
    event_stop_forced = forced_on.to(idle) | forced_full.to(idle)

    event_not_enought_consumption_when_switch_on = sunny_on.to(full) | forced_on.to(
        forced_full
    )

    def __init__(self):
        self.expected_switch_state = False
        super(SolarRouterStateMachine, self).__init__(
            allow_event_without_transition=True
        )

    def on_enter_idle(self):
        self.expected_switch_state = False

    def on_enter_sunny_on(self):
        self.expected_switch_state = True

    def on_enter_sunny_off(self):
        self.expected_switch_state = False

    def on_enter_forced_on(self):
        self.expected_switch_state = True

    def on_enter_full(self):
        self.expected_switch_state = False

    def on_enter_forced_full(self):
        self.expected_switch_state = False


class LogObserver(object):
    def after_transition(self, event, source, target):
        logger.info(f"after: {source.id}--({event})-->{target.id}")

    def on_enter_state(self, target, event):
        logger.info(f"enter: {target.id} from {event}")
