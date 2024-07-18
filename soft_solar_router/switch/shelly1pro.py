"""
set   : "http://${SHELLY}/rpc/Switch.Set?id=0&on=true"  return {"was_on":false}
reset : "http://${SHELLY}/rpc/Switch.Set?id=0&on=false" return{"was_on":false}
status: "http://${SHELLY}/relay/0
return
{
  "ison": true,
  "has_timer": false,
  "timer_started_at": 0,
  "timer_duration": 0.00,
  "timer_remaining": 0.00,
  "source": "WS_in"
}
"""

import requests
from datetime import timedelta
from soft_solar_router.application.interfaces.switch import Switch


class Shelly1Pro(Switch):
    ip_address: str
    device_id: str
    state = None

    def __init__(
        self, history_duration: timedelta, ip_address: str, device_id: str
    ) -> None:
        super().__init__(history_duration)
        self.ip_address = ip_address
        self.device_id = device_id

    def _set(self, state: bool) -> None:
        if state != self.state:
            state_str = "true" if self.state else "false"
            response = requests.get(
                f"http://{self.ip_address}/rpc/Switch.Set"
                f"?id={self.device_id}&on={state_str}"
            )
            response.raise_for_status()
            self.state = state
