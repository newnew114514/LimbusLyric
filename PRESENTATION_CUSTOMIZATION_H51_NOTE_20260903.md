# H51 Presentation Customization — 2026-09-03

H51 is a presentation-only feature layer on top of H50. It does not change player clocks, provider identity, seek authority or automatic-lyric transaction ownership.

## Natural exit effects
The legacy H12/H20 public choices are retained, but H51 replaces the `per_char`, `wipe_ltr` and `wipe_rtl` final drawing path with per-glyph `QPainter.PixmapFragment` opacity/position/scale animation. These modes no longer use a rectangular `setClipRect` wipe. If fragment batching is unavailable the fallback is a whole-row smooth fade, never the old rectangular clip. `shrink` is a smooth eased scale/fade. `fade`, `soft_drift` and `instant` keep their established semantics.

## Center-zone frequency
A 0–100% control determines how often the balanced placement engine is allowed to accept the central ~40% x 44% area. 100% preserves H50 placement behavior. Lower values retry the existing collision-safe placement outside the center; collision safety still wins after a bounded retry count.

## Per-line size range
The range is opt-in and defaults OFF, so the original global font-size control remains authoritative. When enabled, users can choose minimum and maximum point size (6–300 pt). Equal values mean fixed size. A size is chosen only at lyric-row boundaries, so a visible sentence never changes geometry mid-line.

## Script-specific fonts
Optional Japanese, Korean and Western font overrides are applied at lyric-row boundaries using the existing conservative script classifier. Disabled overrides follow the current global/song DIY font. Font coverage is checked; an unsupported override safely falls back to the base font.

## Multi-monitor output
Users can select Primary (automatic) or a concrete `QScreen`. H51 binds the overlay window to that screen and updates its geometry/refresh rate. If a selected display disappears, it falls back to Primary. Live rows are proportionally remapped when switching screens.

## Regression contract
`installer/CHECK_PRESENTATION_CUSTOMIZATION_H51_REPLAY.py` verifies final activation order, per-glyph/no-clip exit rendering, persisted controls, screen binding, center-frequency policy, per-line typography and presentation-only scope.


## Exit compatibility and paint cost

- `fade` (整行淡出) is deliberately not intercepted by H51. It continues through the mature H20/H16 classic fade lifecycle and draw path. `soft_drift` and `instant` also keep their established paths.
- `per_char`, `wipe_ltr`, and `wipe_rtl` reuse the immutable row glyph fragment atlas and submit all visible glyphs with one `QPainter.drawPixmapFragments()` call per fading row, rather than one `drawText()` call per glyph.
- H51 caches immutable exit geometry (font metrics, advances, emphasis offsets, source rectangles, directional order) on the fading row. Per-frame work is limited to current shake offsets, opacity, tiny motion/scale, fragment construction, and one batch submission. A fragment-batch failure degrades to whole-row smooth fade, never rectangular clipping.
