import time
from threading import Lock


class TTLCache:
    """A tiny thread-safe in-memory TTL cache.

    Used to avoid hitting the database / re-serializing the job list on
    every request within a short time window (classic read-through cache).
    """

    def __init__(self):
        self._store: dict[str, tuple[float, object]] = {}
        self._lock = Lock()

    def get(self, key: str):
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            expires_at, value = item
            if time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value, ttl_seconds: int):
        with self._lock:
            self._store[key] = (time.time() + ttl_seconds, value)

    def invalidate(self, key: str | None = None):
        with self._lock:
            if key is None:
                self._store.clear()
            else:
                self._store.pop(key, None)


cache = TTLCache()
