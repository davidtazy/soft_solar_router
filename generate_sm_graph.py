# allow_event_without_transition
from soft_solar_router.application.state_machine import SolarRouterStateMachine

img_path = "doc/soft_solat_state_machine.png"
sm = SolarRouterStateMachine()


sm._graph().write_png(img_path)
