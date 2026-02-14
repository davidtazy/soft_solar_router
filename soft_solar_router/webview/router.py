from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

def create_router(weather, settings, monitoring, persistence):
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        now = datetime.now()
        is_cloudy = False
        # Calculate is_cloudy_tomorrow using weather instance logic if possible
        # Based on application/events.py logic: is_cloudy_tomorrow(now, weather, settings)
        # But we don't have that function imported here.
        # We should import the helper.
        from soft_solar_router.application.events import is_cloudy_tomorrow
        is_cloudy = is_cloudy_tomorrow(now, weather, settings)

        raw_duration = monitoring.get_solar_heater_powered_on_duration()
        
        # Format duration to "Xh Ym"
        total_seconds = int(raw_duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        duration_str = f"{hours}h {minutes}m"

        is_manual = persistence.is_waterheater_on_manually_requested_today(now)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "is_cloudy_tomorrow": is_cloudy,
            "solar_heater_duration": duration_str,
            "is_manual_requested": is_manual
        })

    @router.post("/force")
    async def force_on(request: Request, force_state: bool = Form(False)):
        now = datetime.now()
        persistence.set_manual_request(now, force_state)
        return RedirectResponse(url="/", status_code=303)

    return router
