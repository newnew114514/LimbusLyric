# H88 Inspector Workspace + Cover Fallback + Smooth Navigation

H88 is a presentation-only follow-up to H87 based on real-machine feedback.

- Keeps player, seek, provider and lyric authority unchanged.
- Replaces the active page transition owner with one retiring old-page snapshot; the live new page is revealed underneath, avoiding two full workspace pixmaps blended every animation frame.
- Keeps the refresh-aware H79 timer cadence, so high-refresh displays can still use the existing ~8 ms UI animation tick while 59/60 Hz displays are not asked to render frames they cannot show.
- Makes Subtitle/Motion preview compact by default and adds an explicit expand/collapse control. The choice persists.
- Adds a small section rail for Subtitle/Motion cards with animated scrolling to Preset/Light/Typography and Motion/Sync/Entrance/Direction groups.
- Softens settings-card/control borders to reduce the dense utility-panel feeling without replacing established controls.
- H87 record artwork now uses a QQ + NetEase presentation-only fallback chain, strips UI-only translated suffixes for search, caches successful artwork on disk, backs off repeated failures, and retires a stale previous-track cover after a short grace period.

The real-machine H87 log did not prove a frozen lyric renderer. It showed prolonged periods without a valid QQ transport anchor, followed by normal row births and seek-driven row jumps once UIA proof became available. H88 therefore does not modify lyric rendering or transport authority for that observation.
