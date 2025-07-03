import time
import statistics
from typing import Dict, List, Any
from collections import defaultdict, deque
import threading


class PerformanceMonitor:
    """Monitor and track application performance metrics"""

    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self._response_times = deque(maxlen=max_samples)
        self._analysis_times = defaultdict(lambda: deque(maxlen=max_samples))
        self._request_count = 0
        self._error_count = 0
        self._start_time = time.time()
        self._lock = threading.Lock()

    def record_response_time(self, duration: float):
        """Record total response time"""
        with self._lock:
            self._response_times.append(duration)
            self._request_count += 1

    def record_analysis_time(self, analysis_type: str, duration: float):
        """Record analysis-specific timing"""
        with self._lock:
            self._analysis_times[analysis_type].append(duration)

    def record_error(self):
        """Record an error occurrence"""
        with self._lock:
            self._error_count += 1

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self._lock:
            uptime_hours = (time.time() - self._start_time) / 3600

            # Response time statistics
            response_stats = {}
            if self._response_times:
                response_times_list = list(self._response_times)
                response_stats = {
                    "avg_ms": round(statistics.mean(response_times_list) * 1000, 2),
                    "median_ms": round(statistics.median(response_times_list) * 1000, 2),
                    "min_ms": round(min(response_times_list) * 1000, 2),
                    "max_ms": round(max(response_times_list) * 1000, 2),
                    "p95_ms": round(self._percentile(response_times_list, 95) * 1000, 2),
                    "p99_ms": round(self._percentile(response_times_list, 99) * 1000, 2)
                }

            # Analysis type breakdown
            analysis_breakdown = {}
            for analysis_type, times in self._analysis_times.items():
                if times:
                    times_list = list(times)
                    analysis_breakdown[analysis_type] = {
                        "avg_ms": round(statistics.mean(times_list) * 1000, 2),
                        "count": len(times_list)
                    }

            error_rate = (self._error_count / self._request_count *
                          100) if self._request_count > 0 else 0

            return {
                "uptime_hours": round(uptime_hours, 2),
                "total_requests": self._request_count,
                "error_count": self._error_count,
                "error_rate_percent": round(error_rate, 2),
                "requests_per_hour": round(self._request_count / max(uptime_hours, 0.01), 2),
                "response_times": response_stats,
                "analysis_breakdown": analysis_breakdown
            }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


# Global performance monitor
performance_monitor = PerformanceMonitor()
