"""Dependency-light stabilization core for LimbusLyric.

These modules intentionally avoid Qt/Win32/network ownership.  They define contracts and
normalization helpers so the mature desktop runtime can be migrated without a flag-day rewrite.
"""

from .lyric_model import build_unified_track_from_timeline, split_graphemes, build_line_render_hints, active_line_window
from .search_policy import choose_bilingual_pair, duration_compatible, provider_order
from .local_lyrics import normalize_local_lyric_file, normalize_local_lyric_bytes
from .provider_runtime import (
    LyricQuery, LyricProviderResult, ProviderRegistry, ProviderUnavailable,
)
from .playback_model import PlaybackSnapshot, PlaybackCapabilities
from .fault_journal import FaultJournal, FaultRecord
from .runtime_reliability import CircuitBreaker, CircuitOpen, advancing_time_pair_step

__all__ = [
    "build_unified_track_from_timeline", "split_graphemes", "build_line_render_hints", "active_line_window",
    "choose_bilingual_pair", "duration_compatible", "provider_order",
    "normalize_local_lyric_file", "normalize_local_lyric_bytes",
    "LyricQuery", "LyricProviderResult", "ProviderRegistry", "ProviderUnavailable",
    "PlaybackSnapshot", "PlaybackCapabilities", "FaultJournal", "FaultRecord",
    "CircuitBreaker", "CircuitOpen", "advancing_time_pair_step",
]
