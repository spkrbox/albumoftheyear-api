import threading

from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class Metrics:
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    avg_response_time: float = 0.0
    last_reset: datetime = datetime.now()


class MetricsCollector:
    def __init__(self):
        self._metrics = Metrics()
        self._lock = threading.Lock()
        self._response_times: Dict[str, float] = {}

    def record_request(self, cache_hit: bool = False) -> None:
        with self._lock:
            self._metrics.total_requests += 1
            if cache_hit:
                self._metrics.cache_hits += 1
            else:
                self._metrics.cache_misses += 1

    def record_error(self) -> None:
        with self._lock:
            self._metrics.errors += 1

    def record_response_time(self, duration: float) -> None:
        with self._lock:
            current_avg = self._metrics.avg_response_time
            total = current_avg * (self._metrics.total_requests - 1)
            self._metrics.avg_response_time = (
                total + duration
            ) / self._metrics.total_requests

    def get_metrics(self) -> Metrics:
        with self._lock:
            return self._metrics

    def reset(self) -> None:
        with self._lock:
            self._metrics = Metrics()


metrics = MetricsCollector()
