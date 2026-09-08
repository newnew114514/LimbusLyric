"""Bounded, thread-safe fault journal for refactored runtime boundaries."""
from __future__ import annotations

import threading
import time
import traceback
from collections import deque
from dataclasses import dataclass, asdict
from typing import Any, Deque, Dict, Optional


@dataclass(frozen=True)
class FaultRecord:
    mono_ms: float
    boundary: str
    exc_type: str
    message: str
    detail: str = ""
    traceback_tail: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FaultJournal:
    def __init__(self, capacity: int = 96):
        self._rows: Deque[FaultRecord] = deque(maxlen=max(8, int(capacity)))
        self._lock = threading.Lock()

    def record(self, boundary: str, exc: BaseException, detail: str = "") -> FaultRecord:
        try:
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-5000:]
        except Exception:
            tb = ""
        row = FaultRecord(
            mono_ms=time.monotonic() * 1000.0,
            boundary=str(boundary or "unknown"),
            exc_type=type(exc).__name__,
            message=str(exc),
            detail=str(detail or ""),
            traceback_tail=tb,
        )
        with self._lock:
            self._rows.append(row)
        return row

    def snapshot(self):
        with self._lock:
            return [row.as_dict() for row in self._rows]

    def clear(self):
        with self._lock:
            self._rows.clear()
