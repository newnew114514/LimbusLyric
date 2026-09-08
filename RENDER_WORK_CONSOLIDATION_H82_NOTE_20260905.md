# H82 Render Work Consolidation — 2026-09-05

H82 is a narrow performance/correctness closure layered after H81. It does not rewrite MediaSessionSync, UIA polling, seek authority, or FadingLine exit pixels.

## Evidence that motivated this patch

The H81 Windows log showed genuine frame-budget misses during lyric transitions (single paints above 50 ms and frame spikes above 200 ms) while provider/UIA work remained comparatively small. The same session logged thousands of H61 row-atlas fallback builds. H69 revisited a 12-row prewarm window after every worker completion, while H61's LRU/pixel cap could evict an already-prewarmed row; the next revisit then queued the same row again. This made cache eviction generate new CPU work rather than only a cache miss.

The H74 motion preview also rebuilt QPainterPath text outlines for every glyph on every frame. H79 then drove the preview at a hard-clamped 16 ms even on the tested ~59 Hz display. H82 caches immutable centered glyph/text outlines and per-character advances, uses Qt.PreciseTimer, and rounds the cosmetic preview to the real display period while capping it at 60 Hz. Glow, outline, shadow, transforms and effect equations are unchanged.

## Runtime changes

- H69 future-row prewarm remembers each `(style, text)` key once per concrete lyric timeline. LRU eviction no longer causes the future prewarm loop to rebuild the same row repeatedly. If an evicted row later becomes active, H61's existing active-row path may still rebuild it.
- Queued row-atlas work from an old lyric/timeline is discarded on a new lyric session or concrete timeline epoch. An already-running worker is not killed.
- H74 motion preview caches vector outlines/advances and uses a precise refresh-aligned timer; it does not change desktop lyric rendering.
- H81's transport firewall remains intact. H82 closes one residual startup case: after the historical QQ post-bind grace has already failed, an explicit `startup_existing_attach` may reuse a repeatedly identical, title/artist-matched QQ time-pair duration as a **lyric-version witness only**. This prevents a 239 s already-playing/paused track from displaying a 203 s same-name lyric version. Real track switches still use the older epoch-isolation rules.

## Deliberately unchanged

- `MediaSessionSync._merge_uia_position`, `MediaSessionSync.bind_track`, `AsyncPlayerUiPositionReader.poll`
- `FadingLine.update` / `FadingLine.draw` and all H70/H76 exit semantics
- whole-song 850 ms atlas fuse policy (changing it could reintroduce long build pressure)
- NetEase/KuGou/Spotify clock ownership rules
