import json

import newnet

from .settings import WEATHER_BASE


def current_temp(city):
    """Current temperature reading for `city`."""
    body = newnet.Client().request("GET", f"{WEATHER_BASE}/now?city={city}", timeout_s=2.0, max_attempts=1).raise_for_status().text
    return json.loads(body)["value"]
