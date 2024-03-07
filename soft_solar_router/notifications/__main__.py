from soft_solar_router.notifications.ntfy import Ntfy
import datetime

ntf = Ntfy()

ntf.on_start_sunny(datetime.datetime.now())
