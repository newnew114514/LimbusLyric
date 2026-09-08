# H79 — Live Lyric Shell + Smooth Snapshot Transition

H79 is a presentation-only follow-up to H78 based on field feedback that the 245ms page-wide opacity transition looked low-frame-rate and that `外观` could be mistaken for application appearance.

## User-facing changes

- The creative styling destination is again named **字幕**; the editorial kicker is `LYRICS`.
- Page navigation no longer applies `QGraphicsOpacityEffect` to an entire dense `QScrollArea`. H79 captures the already-laid-out settings region once and animates that frozen surface upward by 10px over 165ms. The overlay deletes itself at completion.
- The transition timer is active only during the micro-animation and is screen-refresh-aware, clamped to 60–120Hz (roughly 16–8ms ticks). This does **not** create a permanent global high-frequency timer.
- H74's small motion preview is changed from a fixed 24ms (~41.7fps) interval to the same refresh-aware interval.
- The Now Playing hero receives a live lyric sample from the already-rendering `LyricWindow.full_text`. Its compact font/color are derived from the existing lyric style.
- A restrained Hero ambient wash uses an already-available cover-follow accent when one exists, otherwise the current lyric text color. H79 does not fetch artwork or start a new worker.

## Performance reasoning

Qt's animation framework normally updates around 60 times per second, but update intervals are not guaranteed. The H78 problem was therefore treated as a composition-cost problem rather than as a numeric FPS setting: animating one cached surface is substantially cheaper than applying an opacity graphics effect to a complex page tree on every frame.

## Boundaries

H79 does not own or modify MediaSessionSync, player seek/clock authority, lyric providers, `FadingLine`, H62–H76 blur lifecycle, config schema, packaging topology, or background acquisition. It adds no thread and no runtime UI library.
