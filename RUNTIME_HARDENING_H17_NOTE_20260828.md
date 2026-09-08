# Runtime Hardening H17 — 2026-08-28

H17 is a narrow reliability closure on top of H16. It does not change QQ/NetEase/KuGou/Spotify time authority, seek arbitration, lyric selection, DIY ownership, or presentation semantics.

## Fixes

1. **All canonical `tasklist` subprocess paths are deadline-bounded.** H11 already bounded the player-liveness fallback. H17 adds the same 0.8s hard deadline to the historical UIA PID lookup and `LyricFetcher` window-title PID lookup, so a wedged Windows `tasklist.exe` cannot strand those workers indefinitely.
2. **NetEase native adapter event-loop lifecycle is restart-safe.** A full `MediaSessionSync` Stop now wakes and releases the retiring `asyncio.Event` and loop references. A later Start on a fresh worker loop creates fresh loop-owned primitives instead of reusing an Event bound to the old loop.
3. **H16 cover-follow result publication is generation-safe.** A single shared result slot/inflight key is replaced by a thread-safe result queue plus per-track request serials. Fast A→B switches and stale same-track completions cannot overwrite a newer result or retire another track's in-flight request. Non-current results may populate cache but cannot recolor the current UI.

Dedicated replay: `installer/CHECK_RUNTIME_HARDENING_H17_REPLAY.py`.
