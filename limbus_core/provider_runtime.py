"""Provider-neutral lyric acquisition contracts.

The module deliberately owns no HTTP, Qt, Win32 or player code.  Provider adapters are
thin duck-typed bridges over the mature host engine.  This gives the monolithic runtime
one stable request/result contract while provider implementations are migrated gradually.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional, Tuple


@dataclass(frozen=True)
class LyricQuery:
    song: str
    artist: str = ""
    provider: str = "网易云"
    trans_only: bool = False
    expected_duration_ms: int = 0
    provider_track_id: Any = None
    provider_duration_ms: int = 0
    prefer_precise: bool = True
    borrow: bool = False

    def normalized(self) -> "LyricQuery":
        return LyricQuery(
            song=str(self.song or "").strip(),
            artist=str(self.artist or "").strip(),
            provider=str(self.provider or "").strip(),
            trans_only=bool(self.trans_only),
            expected_duration_ms=max(0, int(self.expected_duration_ms or 0)),
            provider_track_id=self.provider_track_id,
            provider_duration_ms=max(0, int(self.provider_duration_ms or 0)),
            prefer_precise=bool(self.prefer_precise),
            borrow=bool(self.borrow),
        )


@dataclass
class LyricProviderResult:
    lyric: Optional[str] = None
    translation: Optional[str] = None
    duration_ms: int = 0
    provider: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def legacy_tuple(self) -> Tuple[Optional[str], Optional[str], int]:
        return self.lyric, self.translation, max(0, int(self.duration_ms or 0))


class ProviderUnavailable(LookupError):
    pass


class LegacyProviderAdapter:
    """Calls one mature provider implementation through a stable query contract.

    ``engine`` is intentionally duck typed.  Method lookup happens at *call time* so
    later safety wrappers on the mature provider methods remain effective.
    """

    def __init__(self, name: str, engine: Any):
        self.name = str(name)
        self.engine = engine

    def fetch(self, query: LyricQuery) -> LyricProviderResult:
        q = query.normalized()
        engine = self.engine
        try:
            engine._set_provider_meta(source=self.name, lyric_payload_source=self.name)
        except Exception:
            pass

        ordinary = not q.prefer_precise
        if self.name == "网易云":
            fn = getattr(engine, "_search_netease_ordinary" if ordinary else "search_netease")
            lyric, translation, duration = fn(
                q.song,
                q.artist,
                trans_only=q.trans_only,
                strict_identity=bool(q.borrow),
                expected_duration_ms=int(q.expected_duration_ms or 0),
                preferred_song_id=(q.provider_track_id if not q.borrow else None),
                preferred_duration_ms=(q.provider_duration_ms if not q.borrow else 0),
            )
        elif self.name == "QQ音乐":
            fn = getattr(engine, "_search_qq_ordinary" if ordinary else "search_qq")
            lyric, translation, duration = fn(
                q.song,
                q.artist,
                trans_only=q.trans_only,
                expected_duration_ms=int(
                    q.expected_duration_ms or (q.provider_duration_ms if not q.borrow else 0) or 0
                ),
            )
        elif self.name == "酷狗":
            fn = getattr(engine, "_search_kugou_ordinary" if ordinary else "search_kugou")
            lyric, translation, duration = fn(
                q.song,
                q.artist,
                expected_duration_ms=int(
                    q.expected_duration_ms or (q.provider_duration_ms if not q.borrow else 0) or 0
                ),
                trans_only=q.trans_only,
            )
        else:
            raise ProviderUnavailable(self.name)

        try:
            metadata = dict(engine.last_provider_meta() or {})
        except Exception:
            metadata = {}
        return LyricProviderResult(
            lyric=lyric,
            translation=translation,
            duration_ms=max(0, int(duration or 0)),
            provider=self.name,
            metadata=metadata,
            error=str(getattr(engine, "last_error", "") or ""),
        )


class ProviderRegistry:
    """Small deterministic registry used by the search coordinator."""

    def __init__(self, adapters: Iterable[LegacyProviderAdapter] = ()):  # pragma: no branch
        self._adapters: Dict[str, LegacyProviderAdapter] = {}
        for adapter in adapters:
            self.register(adapter)

    @classmethod
    def from_legacy_engine(cls, engine: Any) -> "ProviderRegistry":
        return cls(LegacyProviderAdapter(name, engine) for name in ("网易云", "QQ音乐", "酷狗"))

    def register(self, adapter: LegacyProviderAdapter) -> None:
        name = str(getattr(adapter, "name", "") or "").strip()
        if not name:
            raise ValueError("provider adapter requires a non-empty name")
        self._adapters[name] = adapter

    def names(self):
        return tuple(self._adapters.keys())

    def fetch(self, query: LyricQuery) -> LyricProviderResult:
        q = query.normalized()
        adapter = self._adapters.get(q.provider)
        if adapter is None:
            raise ProviderUnavailable(q.provider)
        return adapter.fetch(q)
