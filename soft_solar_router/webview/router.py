from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta, timezone
import os

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

def humanize_duration(duration: timedelta) -> str:
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def timeago(date: datetime) -> str:
    now = datetime.now(timezone.utc)
    diff = now - date
    if diff < timedelta(minutes=1):
        return "à l'instant"
    elif diff < timedelta(hours=1):
        return f"il y a {diff.seconds // 60} minutes"
    elif diff < timedelta(days=1):
        return f"il y a {diff.seconds // 3600} heures"
    elif diff < timedelta(days=7):
        return f"il y a {diff.days} jours"
    else:
        return f"il y a {diff.days // 7} semaines"
    

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

        last_night_duration = monitoring.get_solar_heater_powered_on_duration_last_night()
        today_duration = monitoring.get_solar_heater_powered_on_duration_today()

        is_manual = persistence.is_waterheater_on_manually_requested_today(now)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "is_cloudy_tomorrow": is_cloudy,
            "last_night_duration": humanize_duration(last_night_duration),
            "today_duration": humanize_duration(today_duration),
            "is_manual_requested": is_manual,
            "last_time_status_full": timeago(monitoring.get_last_time_status_full())
        })

    @router.post("/force")
    async def force_on(request: Request, force_state: bool = Form(False)):
        now = datetime.now()
        persistence.set_manual_request(now, force_state)
        return RedirectResponse(url="/", status_code=303)

    return router