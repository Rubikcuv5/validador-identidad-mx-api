import time

_store: dict = {}


def get(key: str):
    entry = _store.get(key)
    if entry and time.time() < entry["expires_at"]:
        return entry["value"]
    return None


def set(key: str, value, ttl_seconds: int = 3600):
    _store[key] = {"value": value, "expires_at": time.time() + ttl_seconds}
