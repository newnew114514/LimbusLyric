"""Provider-neutral lyric model helpers.

This module does not parse provider/network formats.  It converts the host's mature
``(start_ms, text, precise_events)`` timeline into a stable dictionary contract and
adds grapheme-level timing as a derived visual hint.  Provider token boundaries remain
authoritative; grapheme timings never replace them.
"""
from __future__ import annotations

import unicodedata
import bisect
from typing import Iterable, List, Sequence

_ZWJ = "\u200d"
_VARIATION_SELECTORS = range(0xFE00, 0xFE10)
_EMOJI_MODIFIERS = range(0x1F3FB, 0x1F400)
_REGIONAL_INDICATORS = range(0x1F1E6, 0x1F200)


def _is_extend(ch: str) -> bool:
    if not ch:
        return False
    cp = ord(ch)
    return (
        unicodedata.combining(ch) != 0
        or unicodedata.category(ch) in {"Mn", "Mc", "Me"}
        or cp in _VARIATION_SELECTORS
        or cp in _EMOJI_MODIFIERS
    )


def split_graphemes(text: str) -> List[str]:
    """Split text into practical Unicode grapheme clusters without extra dependencies.

    It covers combining marks, variation selectors, emoji modifiers, ZWJ sequences and
    regional-indicator flag pairs.  It is deliberately conservative: if uncertain, it
    keeps code points together rather than manufacturing extra lyric timing boundaries.
    """
    s = str(text or "")
    if not s:
        return []
    out: List[str] = []
    current = ""
    ri_count = 0
    join_next = False
    for ch in s:
        cp = ord(ch)
        is_ri = cp in _REGIONAL_INDICATORS
        if not current:
            current = ch
            ri_count = 1 if is_ri else 0
            join_next = ch == _ZWJ
            continue
        if join_next or ch == _ZWJ or _is_extend(ch):
            current += ch
            join_next = ch == _ZWJ
            if is_ri:
                ri_count += 1
            continue
        if is_ri and ri_count == 1:
            current += ch
            ri_count = 2
            join_next = False
            continue
        out.append(current)
        current = ch
        ri_count = 1 if is_ri else 0
        join_next = ch == _ZWJ
    if current:
        out.append(current)
    return out


def _grapheme_timings(token: str, start_ms: int, end_ms: int):
    graphemes = split_graphemes(token)
    if not graphemes:
        return []
    start = max(0, int(start_ms))
    end = max(start, int(end_ms))
    span = max(0, end - start)
    count = len(graphemes)
    rows = []
    for i, glyph in enumerate(graphemes):
        # Integer partition keeps first/last boundaries exact and avoids accumulated drift.
        a = start + (span * i) // count
        b = start + (span * (i + 1)) // count
        rows.append({"text": glyph, "start_ms": a, "end_ms": max(a, b)})
    return rows


def build_line_render_hints(start_ms: int, end_ms: int, next_start_ms=None, words=()):
    """Provider-neutral visual timing hints derived once outside the renderer.

    The values are descriptive only: provider word timings and the mature player clock stay
    authoritative.  Centralizing them avoids each visualizer re-deriving short-line/handoff
    semantics from raw tuples.
    """
    start = max(0, int(start_ms or 0)); end = max(start, int(end_ms or start))
    handoff = None if next_start_ms is None else max(start, int(next_start_ms))
    word_end = start
    for word in list(words or ()):
        try: word_end = max(word_end, int(word.get("end_ms") or start))
        except Exception: pass
    content_end = max(start, word_end if word_end > start else (handoff if handoff is not None else end))
    semantic_end = max(content_end, handoff if handoff is not None else end)
    span = max(0, semantic_end - start)
    return {
        "birth_ms": start,
        "content_end_ms": content_end,
        "handoff_ms": handoff,
        "semantic_end_ms": semantic_end,
        "short_line": bool(span <= 900),
        "preheat_from_ms": max(0, start - min(900, max(260, span // 2 if span else 420))),
    }


def active_line_window(track, position_ms: int, *, history: int = 2, lookahead: int = 2):
    """Return one shared current/history/upcoming slice for visual consumers.

    This mirrors the useful part of Folia's shared visualizer runtime: callers ask one helper
    instead of repeatedly scanning the full lyric list.
    """
    lines = list((track or {}).get("lines") or []) if isinstance(track, dict) else []
    if not lines:
        return {"current_index": -1, "history": (), "current": None, "upcoming": ()}
    starts = []
    for line in lines:
        try: starts.append(max(0, int(line.get("start_ms") or 0)))
        except Exception: starts.append(0)
    pos = max(0, int(position_ms or 0))
    idx = max(0, min(len(lines) - 1, bisect.bisect_right(starts, pos) - 1))
    h = max(0, int(history)); n = max(0, int(lookahead))
    return {
        "current_index": idx,
        "history": tuple(lines[max(0, idx-h):idx]),
        "current": lines[idx],
        "upcoming": tuple(lines[idx+1:min(len(lines), idx+1+n)]),
    }


def build_unified_track_from_timeline(
    timeline: Iterable,
    *,
    song: str = "",
    artist: str = "",
    source: str = "",
    identity: str = "",
    model_version: int = 2,
):
    """Convert the mature host timeline into a stable provider-neutral track dictionary."""
    seq = list(timeline or [])
    lines = []
    for index, item in enumerate(seq):
        try:
            start_ms = max(0, int(item[0]))
            text = str(item[1] or "")
        except Exception:
            continue
        precise = item[2] if isinstance(item, (list, tuple)) and len(item) >= 3 else None
        words = []
        if isinstance(precise, (list, tuple)):
            for ev in precise:
                try:
                    ev_start = int(ev[0])
                    visible_end = int(ev[1])
                    ev_end = int(ev[2]) if len(ev) >= 3 else ev_start
                    visible_start = int(ev[3]) if len(ev) >= 4 else 0
                except Exception:
                    continue
                visible_start = max(0, min(len(text), visible_start))
                visible_end = max(visible_start, min(len(text), visible_end))
                token = text[visible_start:visible_end]
                if not token:
                    continue
                ev_start = max(0, ev_start)
                ev_end = max(ev_start, ev_end)
                words.append({
                    "text": token,
                    "start_ms": ev_start,
                    "end_ms": ev_end,
                    "char_start": visible_start,
                    "char_end": visible_end,
                    # Derived visual timing only.  The token clock remains evidence authority.
                    "graphemes": _grapheme_timings(token, ev_start, ev_end),
                })
        next_start = None
        if index + 1 < len(seq):
            try:
                next_start = max(start_ms, int(seq[index + 1][0]))
            except Exception:
                next_start = None
        precise_end = max((int(w["end_ms"]) for w in words), default=start_ms)
        end_ms = max(start_ms, precise_end, next_start if next_start is not None else start_ms + 4000)
        render_hints = build_line_render_hints(start_ms, end_ms, next_start, words)
        lines.append({
            "index": len(lines),
            "start_ms": start_ms,
            "end_ms": end_ms,
            "text": text,
            "translation": "",
            "romanization": "",
            "role": "MAIN",
            "words": words,
            "render_hints": render_hints,
        })
    return {
        "model_version": int(model_version),
        "identity": str(identity or ""),
        "song": str(song or ""),
        "artist": str(artist or ""),
        "source": str(source or ""),
        "lines": lines,
        "precise_line_count": sum(1 for line in lines if line.get("words")),
        "word_event_count": sum(len(line.get("words") or []) for line in lines),
        "grapheme_event_count": sum(
            len(word.get("graphemes") or [])
            for line in lines
            for word in (line.get("words") or [])
        ),
    }
