"""Stable playback-state contract for the legacy player adapters.

The desktop host currently has several dictionaries produced by GSMTC/UIA/native bridges.
This module normalizes them without deciding transport authority.  Unknown extra keys are
kept in ``extras`` so migration does not destroy diagnostic evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


def _int(value, default=0):
    try:
        return int(round(float(value)))
    except Exception:
        return int(default)




@dataclass(frozen=True)
class PlaybackCapabilities:
    """Observed playback capabilities for one player adapter.

    This is deliberately descriptive, not authoritative: adapters publish what evidence is
    currently available and the mature arbiter still decides which clock wins.  Keeping this
    provider-neutral makes compatibility decisions inspectable without teaching renderers about
    QQ/KuGou/NetEase-specific UIA details.
    """
    player: str = ""
    gsmtc_metadata: bool = False
    gsmtc_timeline: bool = False
    uia_position: bool = False
    local_holdover: bool = False
    visual_rail: bool = False
    gesture_seek: bool = False
    selected_clock: str = ""
    transport_generation: int = 0
    extras: Dict[str, Any] = field(default_factory=dict, compare=False)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None):
        row = dict(value or {})
        known = {
            "player", "gsmtc_metadata", "gsmtc_timeline", "uia_position",
            "local_holdover", "visual_rail", "gesture_seek", "selected_clock",
            "transport_generation",
        }
        return cls(
            player=str(row.get("player") or ""),
            gsmtc_metadata=bool(row.get("gsmtc_metadata", False)),
            gsmtc_timeline=bool(row.get("gsmtc_timeline", False)),
            uia_position=bool(row.get("uia_position", False)),
            local_holdover=bool(row.get("local_holdover", False)),
            visual_rail=bool(row.get("visual_rail", False)),
            gesture_seek=bool(row.get("gesture_seek", False)),
            selected_clock=str(row.get("selected_clock") or ""),
            transport_generation=max(0, _int(row.get("transport_generation"))),
            extras={k: v for k, v in row.items() if k not in known},
        )

    def to_dict(self) -> Dict[str, Any]:
        row = dict(self.extras)
        row.update({
            "player": self.player,
            "gsmtc_metadata": self.gsmtc_metadata,
            "gsmtc_timeline": self.gsmtc_timeline,
            "uia_position": self.uia_position,
            "local_holdover": self.local_holdover,
            "visual_rail": self.visual_rail,
            "gesture_seek": self.gesture_seek,
            "selected_clock": self.selected_clock,
            "transport_generation": self.transport_generation,
        })
        return row


@dataclass(frozen=True)
class PlaybackSnapshot:
    connected: bool = False
    status: str = "unknown"
    position_ms: Optional[int] = None
    duration_ms: int = 0
    position_source: str = ""
    media_title: str = ""
    media_artist: str = ""
    media_source: str = ""
    sync_waiting: bool = False
    captured_mono_ms: float = 0.0
    extras: Dict[str, Any] = field(default_factory=dict, compare=False)

    @classmethod
    def from_legacy(cls, value: Mapping[str, Any] | None, *, captured_mono_ms: float = 0.0):
        row = dict(value or {})
        pos = row.get("position_ms")
        position = None if pos is None else max(0, _int(pos))
        duration = max(0, _int(row.get("duration_ms")))
        status = str(row.get("status") or "unknown").strip().lower()
        if status not in {"playing", "paused", "stopped", "unknown"}:
            status = "unknown"
        known = {
            "connected", "status", "position_ms", "duration_ms", "position_source",
            "media_title", "media_artist", "media_source", "sync_waiting",
        }
        return cls(
            connected=bool(row.get("connected", False)),
            status=status,
            position_ms=position,
            duration_ms=duration,
            position_source=str(row.get("position_source") or ""),
            media_title=str(row.get("media_title") or ""),
            media_artist=str(row.get("media_artist") or ""),
            media_source=str(row.get("media_source") or ""),
            sync_waiting=bool(row.get("sync_waiting", False)),
            captured_mono_ms=float(captured_mono_ms or 0.0),
            extras={k: v for k, v in row.items() if k not in known},
        )

    def to_legacy(self) -> Dict[str, Any]:
        row = dict(self.extras)
        row.update({
            "connected": bool(self.connected),
            "status": str(self.status),
            "position_ms": self.position_ms,
            "duration_ms": int(self.duration_ms),
            "position_source": str(self.position_source),
            "media_title": str(self.media_title),
            "media_artist": str(self.media_artist),
            "media_source": str(self.media_source),
            "sync_waiting": bool(self.sync_waiting),
        })
        return row

    def position_at(self, mono_ms: float | None = None) -> Optional[int]:
        """Return a sampled/extrapolated position without mutating the snapshot.

        Mirrors the sampledAt-style contract used by robust external-player APIs: while playing,
        a trusted sample can advance locally using monotonic time; paused/stopped samples stay
        fixed.  ``playback_rate`` may be supplied through ``extras`` by legacy adapters.
        """
        if self.position_ms is None:
            return None
        pos = max(0, int(self.position_ms))
        if self.status != "playing" or self.captured_mono_ms <= 0:
            return min(pos, self.duration_ms) if self.duration_ms > 0 else pos
        try:
            now = float(self.captured_mono_ms if mono_ms is None else mono_ms)
            rate = max(0.01, float(self.extras.get("playback_rate") or 1.0))
            pos = int(round(pos + max(0.0, now - float(self.captured_mono_ms)) * rate))
        except Exception:
            pass
        if self.duration_ms > 0:
            pos = min(pos, int(self.duration_ms))
        return max(0, pos)

    def sampled_dict(self, mono_ms: float | None = None) -> Dict[str, Any]:
        row = self.to_legacy()
        row["sampled_at_mono_ms"] = float(self.captured_mono_ms or 0.0)
        row["sampled_position_ms"] = self.position_at(mono_ms)
        return row

    @property
    def track_key(self):
        return (
            self.media_title.strip().casefold(),
            self.media_artist.strip().casefold(),
            self.media_source.strip().casefold(),
            int(self.duration_ms or 0),
        )

    @property
    def has_clock(self) -> bool:
        return self.position_ms is not None and self.duration_ms > 0
