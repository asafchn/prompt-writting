import json

import newnet

from .settings import PROFILE_BASE


def load_user(uid):
    """User record as a dict. Errors propagate to the caller."""
    data = json.loads(newnet.Client().request(
        "GET", f"{PROFILE_BASE}/users/{uid}", timeout_s=0.9, max_attempts=5
    ).raise_for_status().text)
    return {"id": uid, "score": data["value"], "tags": data["items"]}
