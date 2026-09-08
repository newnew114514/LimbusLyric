"""Small runtime reliability primitives used by R2.

This module intentionally has no Qt, Win32, requests, or player dependencies.  It only owns
state-machine mechanics that are safe to replay in isolation.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Dict, Optional, Tuple
import time


class CircuitOpen(RuntimeError):
    """Raised when an external provider is temporarily suppressed after repeated failures."""


@dataclass
class _CircuitState:
    failures: int = 0
    open_until_ms: float = 0.0
    last_failure_ms: float = 0.0


class CircuitBreaker:
    """Tiny keyed circuit breaker for repeated upstream 5xx/429 failures.

    The breaker is deliberately policy-free: callers decide which failures count.  Successful
    calls reset a key immediately.  ``allow`` never sleeps; it simply makes retry ownership
    explicit so a failing provider cannot serialize every fallback path.
    """

    def __init__(self, threshold: int = 2, open_ms: int = 45000):
        self.threshold = max(1, int(threshold))
        self.open_ms = max(1000, int(open_ms))
        self._states: Dict[str, _CircuitState] = {}
        self._lock = Lock()

    @staticmethod
    def _now_ms(now_ms: Optional[float] = None) -> float:
        return float(now_ms if now_ms is not None else time.monotonic() * 1000.0)

    def allow(self, key: str = "default", now_ms: Optional[float] = None) -> bool:
        now = self._now_ms(now_ms)
        k = str(key or "default")
        with self._lock:
            state = self._states.get(k)
            if state is None:
                return True
            if state.open_until_ms > now:
                return False
            if state.open_until_ms:
                # Half-open without a background timer: one caller is allowed to probe.
                state.open_until_ms = 0.0
                state.failures = max(0, self.threshold - 1)
            return True

    def require(self, key: str = "default", now_ms: Optional[float] = None) -> None:
        if not self.allow(key, now_ms=now_ms):
            snap = self.snapshot(key, now_ms=now_ms)
            raise CircuitOpen(
                f"circuit open for {key}: retry_after_ms={int(snap.get('retry_after_ms', 0))}"
            )

    def success(self, key: str = "default") -> None:
        k = str(key or "default")
        with self._lock:
            self._states.pop(k, None)

    def failure(self, key: str = "default", now_ms: Optional[float] = None) -> bool:
        now = self._now_ms(now_ms)
        k = str(key or "default")
        with self._lock:
            state = self._states.setdefault(k, _CircuitState())
            state.failures += 1
            state.last_failure_ms = now
            if state.failures >= self.threshold:
                state.open_until_ms = max(state.open_until_ms, now + float(self.open_ms))
                return True
            return False

    def snapshot(self, key: str = "default", now_ms: Optional[float] = None) -> dict:
        now = self._now_ms(now_ms)
        k = str(key or "default")
        with self._lock:
            state = self._states.get(k) or _CircuitState()
            return {
                "failures": int(state.failures),
                "open": bool(state.open_until_ms > now),
                "retry_after_ms": max(0.0, float(state.open_until_ms) - now),
                "last_failure_ms": float(state.last_failure_ms),
            }


def advancing_time_pair_step(
    pending: Optional[dict],
    position_ms: float,
    duration_ms: int,
    now_ms: float,
    status: str,
    source_key: str,
    *,
    min_samples: int = 4,
    min_span_ms: float = 1200.0,
    min_progress_ms: float = 800.0,
    max_gap_ms: float = 1800.0,
    max_pace_error_ms: float = 1300.0,
) -> Tuple[Optional[dict], bool]:
    """Prove a whole-second UI time-pair is the *advancing* playback clock.

    This is stricter than ordinary two-sample geometry validation because QQ hover preview shares
    the same text surface.  It proves duration/clock eligibility only; it never grants seek
    authority.
    """
    if str(status or "").lower() != "playing":
        return None, False
    try:
        pos = float(position_ms)
        dur = int(duration_ms or 0)
        now = float(now_ms)
        if dur < 15000 or pos < 0 or pos > dur + 1200:
            return None, False
        key = str(source_key or "")
        p = pending if isinstance(pending, dict) else None
        if p is not None:
            same_key = (not p.get("source_key") or not key or str(p.get("source_key")) == key)
            same_duration = abs(float(p.get("duration_ms", dur)) - float(dur)) <= 1200.0
            gap = max(0.0, now - float(p.get("last_mono", now)))
            last_pos = float(p.get("last_position_ms", pos))
            expected = last_pos + gap
            coherent = (
                same_key and same_duration and 0.0 <= gap <= float(max_gap_ms) and
                pos >= last_pos - 80.0 and abs(pos - expected) <= float(max_pace_error_ms)
            )
            if not coherent:
                p = None
        if p is None:
            return {
                "source_key": key,
                "duration_ms": dur,
                "first_position_ms": pos,
                "last_position_ms": pos,
                "first_mono": now,
                "last_mono": now,
                "samples": 1,
            }, False
        p["samples"] = int(p.get("samples", 1)) + 1
        p["last_position_ms"] = pos
        p["last_mono"] = now
        span = max(0.0, now - float(p.get("first_mono", now)))
        progress = pos - float(p.get("first_position_ms", pos))
        pace_ok = abs(progress - span) <= float(max_pace_error_ms)
        proven = bool(
            int(p.get("samples", 0)) >= int(min_samples) and
            span >= float(min_span_ms) and progress >= float(min_progress_ms) and pace_ok
        )
        return p, proven
    except Exception:
        return None, False
