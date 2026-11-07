import json

import oldnet

from .settings import WEATHER_BASE


def current_temp(city):
    """Current temperature reading for `city`."""
    body = oldnet.fetch(f"{WEATHER_BASE}/now?city={city}", 2000)
    return json.loads(body)["value"]
