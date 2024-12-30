from typing import Any, Optional
from datetime import datetime, timedelta
from collections import OrderedDict
import threading


class LRUCache:
    def __init__(self, max_size: int = 5000, ttl: timedelta = timedelta(hours=1)):
        self._cache = OrderedDict()
        self._expiry = {}
        self._max_size = max_size
        self._ttl = ttl
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None

            if datetime.now() >= self._expiry[key]:
                self._remove(key)
                return None

            # move to end (most recently used)
            value = self._cache.pop(key)
            self._cache[key] = value
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self._cache:
                self._cache.pop(key)
            elif len(self._cache) >= self._max_size:
                # remove least recently used item
                oldest_key = next(iter(self._cache))
                self._remove(oldest_key)

            self._cache[key] = value
            self._expiry[key] = datetime.now() + self._ttl

    def _remove(self, key: str) -> None:
        self._cache.pop(key, None)
        self._expiry.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._expiry.clear()


cache = LRUCache()
