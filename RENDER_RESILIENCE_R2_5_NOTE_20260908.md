# Render Resilience R2.5 — 2026-09-08

Renderer-only follow-up to R2.4. Playback/player adapters, lyric provider/search, seek authority, UI layout and critical wrapper topology are unchanged.

Changes:
- Held/history fragment batching now compiles immutable glyph geometry, wrap decisions, source rects, scale and conservative bounds once per stable row/transform. Living per-glyph shake remains sampled every frame.
- H51 script-font coverage checks use an LRU keyed by representative codepoints and a cached font-family set. Import/load/reload of app-private fonts invalidates the cache.
- Whole-song atlas performance fuse is tied to the style/font signature that exceeded the budget. A different style clears the global fuse immediately; the same failed style receives a 120 s cooldown before retry.
- Added a dedicated R2.5 release gate and preserved RC11 critical wrapper assignment counts.

Field motivation: R2.4 log showed ~99% sprite hits while 3 resident rows / 2 history rows still spent ~12.5 ms per paint, and 4 visual rows / 2 history / 1 fading reached 14.47 ms average / 25.69 ms p95. This patch targets repeated row-layout work and custom-font cache poisoning rather than disabling visual effects.
