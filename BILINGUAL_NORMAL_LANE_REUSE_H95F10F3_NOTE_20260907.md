# H95F10F3 — Bilingual normal-lane reuse

## Problem confirmed from field telemetry

The bilingual translation provider/alignment path was already returning cached same-provider text (`network-refetch=0`), but H95F10F2 made the visible secondary lane rebuild/transform styled `QPainterPath` glyph geometry on every paint. On the captured 59 Hz system the bilingual renderer crossed the hard paint budget repeatedly (hundreds of milliseconds), while provider work remained off the GUI hot path.

H95F10F2 also mapped each translated glyph to a primary precise glyph for active reveal and exit. That is not the intended product model: translated Chinese/Japanese/English text may have a different character count and should behave like the existing translation-only ordinary-LRC presentation, not like a second copy of the source provider's word clock.

## Narrow repair

H95F10F3 deliberately leaves the mature primary lyric renderer untouched:

- precise main lyrics continue through the existing precise/provider timing path;
- classic main lyrics continue through the existing ordinary/classic path;
- the bilingual translation lane reads only the current line index + authoritative playback position and computes its own ordinary-LRC character cadence from that line's timestamps and translated text length;
- active/history translated glyphs use the mature high-DPI glyph sprite cache instead of per-frame vector path construction;
- translation history uses translation-owned per-character/wipe ordering rather than primary glyph mapping;
- no second full-song translation atlas is scheduled;
- a bounded, pressure-aware GUI-idle sprite prewarm spreads first-use raster cost instead of concentrating it in a paint event.

The secondary lane is therefore logically equivalent to “normal translation-only presentation attached under the current main row” without creating a second LyricWindow or a second playback clock.

## Authority boundaries intentionally unchanged

H95F10F3 does not replace or modify `MediaSessionSync.position`, seek handling, QQ startup anchoring, provider search/fetch, LRC parsing, precision upgrades, `LyricWindow.paintEvent`, `FadingLine.draw`, packaging dependencies, or config schema. H95F10F2 startup-anchor and final dirty-region fixes remain active.

## Regression gate

`installer/CHECK_BILINGUAL_NORMAL_LANE_REUSE_H95F10F3_REPLAY.py` verifies the *final effective owner*, not merely the historical H95F10F2 function body. It rejects primary-glyph mapping and QPainterPath construction in the final translation hot path, checks line index 0 explicitly, checks translated-length-dependent ordinary cadence, checks bounded prewarm/no translated full-song atlas, and protects timing/parser/provider authority.

## Whole-project review notes / intentionally not refactored

The release replay suite passes with H95F10F3, but several architectural risks remain and were deliberately *not* rewritten in this repair:

- The monolith has many layered final-owner patches (currently 18 `ControlPanel.__init__` assignments, 6 `FadingLine.draw` assignments, 4 `LyricWindow.paintEvent` assignments). Their replay locks reduce regression risk but make future final-owner changes easy to misunderstand.
- H95F7 still suppresses legacy duplicate bilingual painting by temporarily replacing global `_h95f5_translation_for_line` during the primary paint and restoring it in `finally`. Qt painting is GUI-threaded and the current gate chain passes, but this is a re-entrancy/maintenance hazard; replacing it safely requires a dedicated renderer-ownership refactor, not a side effect of this performance fix.
- The whole-song atlas performance fuse is shared renderer infrastructure. Once a costly build trips the fuse, later rendering intentionally falls back to glyph sprites. H95F10F3 does not reset or bypass that fuse.
- H95F10F3's translated sprite prewarm is deliberately one glyph at a time, pressure-aware, and spaced at 60 ms. It reduces seek/first-use bursts but still performs QPixmap-compatible raster work on the GUI thread; field telemetry should confirm it does not create small periodic stalls on unusually expensive fonts.
- The historical H95F10F2 replay still validates the H95F10F2 layer-local implementation for archaeology. The new H95F10F3 replay separately validates the *final effective owner* so an older layer cannot accidentally dictate current bilingual semantics.

No provider transport, QQ/Kugou/NetEase clock authority, parsing, precision upgrade, config schema, dependency pin, or Windows packaging route was changed as part of this repair.
