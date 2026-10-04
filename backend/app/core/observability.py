import os
import re
import json
import time
import logging
import threading
from collections import deque
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

from app.core.logging_filter import mask_pii

# Context variables for correlation across async tasks and threads
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
entry_point_ctx: ContextVar[str] = ContextVar("entry_point", default="")

# Sensitive key redaction regex patterns
API_KEY_REGEX = re.compile(r'((?:(?:\b|[?&])(?:key|api_key))\s*=\s*)[^& \s"\']+', re.IGNORECASE)
HEADER_KEY_REGEX = re.compile(r'((?:x-goog-api-key|x-internal-secret|authorization)\s*[:=]\s*["\']?(?:Bearer\s+)?)[^"\'\s&]+', re.IGNORECASE)


def sanitize_log_str(text: str) -> str:
    """Sanitizes text by removing PII and secret tokens/keys."""
    if not isinstance(text, str):
        return str(text)
    text = mask_pii(text)
    text = API_KEY_REGEX.sub(r'\1[REDACTED]', text)
    text = HEADER_KEY_REGEX.sub(r'\1[REDACTED]', text)
    return text


def get_request_id() -> str:
    return request_id_ctx.get() or "req-none"


def get_entry_point() -> str:
    return entry_point_ctx.get() or "unknown"


def set_request_context(request_id: str, entry_point: str):
    request_id_ctx.set(request_id)
    entry_point_ctx.set(entry_point)


class JsonLogFormatter(logging.Formatter):
    """Zero-dependency JSON log formatter for structured cloud logs on Render."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Format message safely
        try:
            msg = record.getMessage()
        except Exception:
            msg = str(record.msg)
            
        sanitized_msg = sanitize_log_str(msg)

        log_dict: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": sanitized_msg,
            "request_id": get_request_id(),
            "entry_point": get_entry_point(),
        }

        # Include structured event payload if present
        if hasattr(record, "structured_data") and isinstance(record.structured_data, dict): # type: ignore[attr-defined]
            for k, v in record.structured_data.items(): # type: ignore[attr-defined]
                if isinstance(v, str):
                    log_dict[k] = sanitize_log_str(v)
                else:
                    log_dict[k] = v

        if record.exc_info:
            log_dict["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_dict, ensure_ascii=False)


events_logger = logging.getLogger("lumina.events")


def log_event(event_name: str, level: int = logging.INFO, **kwargs: Any) -> None:
    """Emits a structured JSON event to stdout."""
    sanitized_kwargs: Dict[str, Any] = {}
    for k, v in kwargs.items():
        if isinstance(v, str):
            sanitized_kwargs[k] = sanitize_log_str(v)
        elif isinstance(v, (int, float, bool)) or v is None:
            sanitized_kwargs[k] = v
        else:
            sanitized_kwargs[k] = sanitize_log_str(str(v))

    structured_data = {
        "event": event_name,
        **sanitized_kwargs
    }
    
    # Log via standard logging system with structured extra
    events_logger.log(
        level,
        f"[Event: {event_name}]",
        extra={"structured_data": structured_data}
    )


# ==============================================================================
# In-Memory RED Metrics & SLO Engine (512 MB Safe, Zero External Libraries)
# ==============================================================================

class MetricsTracker:
    """Thread-safe, bounded, zero-dependency in-memory metrics store.
    Tracks Rate, Errors (5xx), Duration (p50/p95/p99) and SLO health over rolling windows.
    """

    def __init__(self, sample_limit: int = 1000):
        self._lock = threading.Lock()
        self._sample_limit = sample_limit
        self._durations: deque[float] = deque(maxlen=sample_limit)
        
        # Bounded route/status counters: {(route, method, status_class): count}
        self._counts: Dict[Tuple[str, str, str], int] = {}
        
        # Rolling 5m window for requests: deque of (epoch_seconds, is_5xx)
        self._requests_5m: deque[Tuple[float, bool]] = deque()
        
        # Rolling 15m window for AI calls: deque of (epoch_seconds, is_fallback, reason)
        self._ai_calls_15m: deque[Tuple[float, bool, str]] = deque()
        
        # Dependency calls stats: {dep_name: {"total": int, "success": int, "error": int, "durations": deque}}
        self._dependency_stats: Dict[str, Dict[str, Any]] = {}

    def _normalize_route(self, route: str) -> str:
        """Normalizes dynamic path parameters to bounded route templates."""
        # Replace UUIDs / hashes / patient IDs / numbers in path
        clean = re.sub(r'/(?:[0-9a-fA-F-]{8,}|[0-9]{4,}|[a-zA-Z0-9_\-\.]+@(?:s\.whatsapp\.net|c\.us))', '/:id', route)
        # Strip query string
        clean = clean.split('?')[0].rstrip('/')
        return clean or "/"

    def record_request(self, route: str, method: str, status_code: int, duration_ms: float) -> None:
        now = time.time()
        norm_route = self._normalize_route(route)
        method_str = method.upper()
        
        status_class = f"{status_code // 100}xx"
        is_5xx = (500 <= status_code < 600)

        with self._lock:
            # 1. Total counters
            key = (norm_route, method_str, status_class)
            self._counts[key] = self._counts.get(key, 0) + 1

            # 2. Duration ring buffer
            self._durations.append(duration_ms)

            # 3. Rolling 5m window
            self._requests_5m.append((now, is_5xx))
            # Prune events older than 300s (5m)
            cutoff_5m = now - 300.0
            while self._requests_5m and self._requests_5m[0][0] < cutoff_5m:
                self._requests_5m.popleft()

    def record_ai_call(self, is_fallback: bool, reason: str = "") -> None:
        now = time.time()
        with self._lock:
            self._ai_calls_15m.append((now, is_fallback, reason))
            # Prune events older than 900s (15m)
            cutoff_15m = now - 900.0
            while self._ai_calls_15m and self._ai_calls_15m[0][0] < cutoff_15m:
                self._ai_calls_15m.popleft()

    def record_dependency(self, dependency: str, duration_ms: float, outcome: str, error_type: Optional[str] = None) -> None:
        dep_key = dependency.lower()
        with self._lock:
            if dep_key not in self._dependency_stats:
                self._dependency_stats[dep_key] = {
                    "total": 0,
                    "success": 0,
                    "error": 0,
                    "durations": deque(maxlen=200),
                    "last_error": None,
                }
            stats = self._dependency_stats[dep_key]
            stats["total"] += 1
            if outcome == "success":
                stats["success"] += 1
            else:
                stats["error"] += 1
                stats["last_error"] = error_type or "UnknownError"
            stats["durations"].append(duration_ms)

    def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        if not values:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        s = sorted(values)
        n = len(s)
        def get_p(pct: float) -> float:
            idx = int(n * pct)
            if idx >= n:
                idx = n - 1
            return round(s[idx], 2)
        return {
            "p50": get_p(0.50),
            "p95": get_p(0.95),
            "p99": get_p(0.99),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns comprehensive RED metrics summary (Protected)."""
        now = time.time()
        with self._lock:
            durations_list = list(self._durations)
            latency_pct = self._calculate_percentiles(durations_list)
            
            # Format route counts
            route_stats: List[Dict[str, Any]] = []
            for (route, meth, sc), cnt in self._counts.items():
                route_stats.append({
                    "route": route,
                    "method": meth,
                    "status_class": sc,
                    "count": cnt
                })

            # Dependencies summary
            dep_summary: Dict[str, Any] = {}
            for dep, st in self._dependency_stats.items():
                dep_durs = list(st["durations"])
                dep_summary[dep] = {
                    "total": st["total"],
                    "success": st["success"],
                    "error": st["error"],
                    "success_rate_pct": round((st["success"] / st["total"] * 100.0), 1) if st["total"] > 0 else 100.0,
                    "latency": self._calculate_percentiles(dep_durs),
                    "last_error": st["last_error"]
                }

            # AI Fallback stats (last 15m)
            total_ai = len(self._ai_calls_15m)
            fallbacks = sum(1 for _, fb, _ in self._ai_calls_15m if fb)
            fallback_pct = round((fallbacks / total_ai * 100.0), 1) if total_ai > 0 else 0.0

            # 5xx in 5m
            total_req_5m = len(self._requests_5m)
            err_5m = sum(1 for _, is_5xx in self._requests_5m if is_5xx)
            err_5m_pct = round((err_5m / total_req_5m * 100.0), 2) if total_req_5m > 0 else 0.0

            return {
                "uptime_samples": len(durations_list),
                "latency_ms": latency_pct,
                "requests_5m": {
                    "total": total_req_5m,
                    "5xx_errors": err_5m,
                    "error_rate_pct": err_5m_pct
                },
                "ai_inference_15m": {
                    "total": total_ai,
                    "fallbacks": fallbacks,
                    "fallback_rate_pct": fallback_pct
                },
                "dependencies": dep_summary,
                "routes": route_stats
            }

    def check_slo(self) -> Tuple[bool, Dict[str, Any]]:
        """Evaluates Service Level Objectives (SLO).
        Returns:
            is_healthy: bool (True for 200 OK, False for 503 Service Unavailable)
            details: Dict[str, Any] (Symptom-based metrics, no PII)
        """
        now = time.time()
        with self._lock:
            # Clean old items
            cutoff_5m = now - 300.0
            while self._requests_5m and self._requests_5m[0][0] < cutoff_5m:
                self._requests_5m.popleft()

            cutoff_15m = now - 900.0
            while self._ai_calls_15m and self._ai_calls_15m[0][0] < cutoff_15m:
                self._ai_calls_15m.popleft()

            total_5m = len(self._requests_5m)
            err_5m = sum(1 for _, is_5xx in self._requests_5m if is_5xx)
            err_rate = (err_5m / total_5m) if total_5m > 0 else 0.0

            durations_list = list(self._durations)
            latency = self._calculate_percentiles(durations_list)

            total_ai = len(self._ai_calls_15m)
            fallbacks = sum(1 for _, fb, _ in self._ai_calls_15m if fb)
            ai_fallback_rate = (fallbacks / total_ai) if total_ai > 0 else 0.0

            # SLO Rules:
            # 1. Page (503): 5xx error rate > 5% in rolling 5 min window (with min 10 requests to avoid noise)
            # 2. Degraded (200 with degraded=true): AI fallback rate > 20% in rolling 15 min window
            is_healthy = True
            unhealthy_reason = None
            if total_5m >= 10 and err_rate > 0.05:
                is_healthy = False
                unhealthy_reason = f"5xx error rate exceeded 5% ({round(err_rate * 100, 1)}%) in 5m window"

            is_degraded = (total_ai >= 5 and ai_fallback_rate > 0.20)

            result = {
                "status": "healthy" if is_healthy else "unhealthy",
                "degraded": is_degraded,
                "error_rate_5m_pct": round(err_rate * 100.0, 2),
                "requests_5m_count": total_5m,
                "p95_latency_ms": latency["p95"],
                "ai_fallback_rate_15m_pct": round(ai_fallback_rate * 100.0, 1),
            }
            if unhealthy_reason:
                result["reason"] = unhealthy_reason
            return is_healthy, result


# Global singleton instance
metrics_tracker = MetricsTracker()


# ==============================================================================
# Dual Synchronous & Asynchronous Dependency Tracker
# ==============================================================================

class track_dependency:
    """Universal dependency tracking context manager.
    Works seamlessly with both `with track_dependency('groq'):` and
    `async with track_dependency('meta_graph'):`.
    """

    def __init__(self, name: str):
        self.name = name
        self.start_time: float = 0.0
        self.outcome: str = "success"
        self.error_type: Optional[str] = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000.0
        if exc_type is not None:
            self.outcome = "error"
            self.error_type = exc_type.__name__
        metrics_tracker.record_dependency(
            dependency=self.name,
            duration_ms=duration_ms,
            outcome=self.outcome,
            error_type=self.error_type
        )
        log_event(
            event_name="dependency_call",
            dependency=self.name,
            duration_ms=round(duration_ms, 2),
            outcome=self.outcome,
            error_type=self.error_type
        )
        return False  # Do not suppress exceptions

    async def __aenter__(self):
        self.start_time = time.perf_counter()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000.0
        if exc_type is not None:
            self.outcome = "error"
            self.error_type = exc_type.__name__
        metrics_tracker.record_dependency(
            dependency=self.name,
            duration_ms=duration_ms,
            outcome=self.outcome,
            error_type=self.error_type
        )
        log_event(
            event_name="dependency_call",
            dependency=self.name,
            duration_ms=round(duration_ms, 2),
            outcome=self.outcome,
            error_type=self.error_type
        )
        return False


def setup_observability_logging() -> None:
    """Configures structured JSON logging on root and application loggers."""
    log_format = os.getenv("LOG_FORMAT", "json").lower()
    root = logging.getLogger()
    
    # Silence verbose HTTP connection loggers to prevent query string key leaks
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if log_format == "json":
        formatter = JsonLogFormatter()
        for handler in root.handlers:
            handler.setFormatter(formatter)
        if not root.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            root.addHandler(handler)
        root.setLevel(logging.INFO)
