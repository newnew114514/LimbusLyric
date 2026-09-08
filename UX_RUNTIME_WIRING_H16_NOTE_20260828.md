# UX RUNTIME WIRING H16 — 2026-08-28

## Evidence
H15 real-machine testing exposed presentation controls whose UI state did not fully own runtime behavior. The attached H15 log confirms the new liveness isolation is active and also shows `visible_stack=3 / live_count=3 / history_count=2`, so the subtitle-capacity engine itself is working; the misleading part was the label and the independent fading lane.

## H16 closure
- Font size remains a `QSpinBox` but is now direct keyboard input over a safe 6–300 pt range. The raw saved value is restored after legacy initialization so values above 100 are not clamped on restart. Runtime changes queue the normal visual-style update and save normally.
- Continuous H12 font weight is now reapplied inside the normal style resolver. A per-song DIY `font_bold` rule still wins; otherwise a 1–99 global weight survives lyric restart/start.
- Exit effects now own a wall-clock presentation lifetime. Every effect except explicit `instant` remains perceptible for at least about 520 ms normally and about 380 ms under accelerated pressure, while preserving the existing fade-speed setting when it is slower. Player position/timing is not delayed.
- Cover-follow uses the current NetEase provider song id when available, otherwise exact title + multi-artist matching. Failed lookup retries at 2/6/18 seconds instead of being permanently suppressed. A successful color is track-owned and participates in `_resolved_active_visual_style`, so later Start/restart cannot overwrite it with the global color. Per-song DIY color remains higher priority.
- Cover-follow and per-song random color are mutually exclusive. Existing configurations with both enabled are normalized to cover-follow when H16 starts.
- The old `桌面同时字幕` label is renamed to `清晰保留字幕`: it controls current + fully readable history (1–6). Exit animation is a separate transition lane and may briefly add visual rows. Increasing capacity fills from later line changes; deleted old rows are not resurrected.
- H12 timers are retained; H16 replaces only presentation polling and cover lookup callbacks. H15 updater polling still runs through the existing H15 wrapper.

## Non-goals / authority boundary
H16 does not assign or modify `MediaSessionSync` transport methods, `LyricSearchEngine.search`, auto-track result ownership, QQ Software-2, NetEase native clock, KuGou golden transport, Spotify GSMTC authority, V28 visual handoff, or V29 transport generation.

## Gate
Dedicated gate: `installer/CHECK_UX_RUNTIME_WIRING_H16_REPLAY.py`.
Canonical suite after H16: **74 gates**.
