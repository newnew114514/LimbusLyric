"""Pure deterministic lyric-provider selection policy.

Keeping these decisions outside network/provider code makes them replayable and prevents
later provider patches from silently changing ranking semantics.
"""
from __future__ import annotations

KNOWN_PROVIDERS = ("网易云", "QQ音乐", "酷狗")


def duration_compatible(expected_ms, candidate_ms, *, floor_ms: int = 3500, ratio: float = 0.025) -> bool:
    try:
        expected = int(expected_ms or 0)
        candidate = int(candidate_ms or 0)
    except Exception:
        return False
    if not expected or not candidate:
        return True
    return abs(expected - candidate) <= max(int(floor_ms), int(max(expected, candidate) * float(ratio)))


def provider_order(preferred: str = ""):
    preferred = str(preferred or "")
    return tuple(([preferred] if preferred else []) + [p for p in KNOWN_PROVIDERS if p != preferred])


def choose_bilingual_pair(candidates, preferred_source: str = "", prefer_precise: bool = False):
    rows = [row for row in list(candidates or []) if isinstance(row, dict)]
    if not rows:
        return None
    pool = rows
    if bool(prefer_precise):
        max_quality = max(int(row.get("quality", 0) or 0) for row in rows)
        if max_quality >= 3:
            pool = [row for row in rows if int(row.get("quality", 0) or 0) == max_quality]
    return max(pool, key=lambda row: (
        round(float(row.get("coverage", 0.0) or 0.0), 3),
        1 if str(row.get("provider") or "") == str(preferred_source or "") else 0,
        int(row.get("trans_rows", 0) or 0),
        int(row.get("quality", 0) or 0),
        -KNOWN_PROVIDERS.index(str(row.get("provider") or "")) if str(row.get("provider") or "") in KNOWN_PROVIDERS else -99,
    ))
