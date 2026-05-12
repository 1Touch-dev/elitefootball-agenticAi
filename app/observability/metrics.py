import time
from collections import defaultdict
from typing import Dict

class MetricsRegistry:
    """Operational dashboard backing container anchoring throughput telemetry."""
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._histograms: Dict[str, list] = defaultdict(list)

    def increment(self, name: str, count: int = 1):
        self._counters[name] += count

    def record_latency(self, name: str, start_time: float):
        elapsed = time.time() - start_time
        self._histograms[name].append(elapsed)

    def export_snapshot(self):
        """Provides snapshot formatting ready for dynamic prometheus consumption."""
        return {
            "counters": dict(self._counters),
            "average_latencies": {
                k: sum(v)/len(v) if v else 0 for k, v in self._histograms.items()
            }
        }

# Global default observability bucket
metrics = MetricsRegistry()
