import json

import oldnet

from .settings import PROFILE_BASE


def load_user(uid):
    """User record as a dict. Errors propagate to the caller."""
    data = json.loads(oldnet.fetch(f"{PROFILE_BASE}/users/{uid}", timeout_ms=900, retries=4))
    return {"id": uid, "score": data["value"], "tags": data["items"]}
