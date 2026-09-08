# H95F10F8 — Sync UI / Cold Raster / Precise Pair Priority

Field evidence from the audited F7 Windows run exposed three residual issues that static replay did not reproduce:

1. The retired H75 four-player sync rows were visually hidden but could still leave empty row geometry in the final settings card. H95F10F6 also collapsed the mature Sync Doctor although the user wanted those expert controls visible.
2. Once the full-song atlas performance fuse fired, a newly visible row could enter the synchronous sprite/vector fallback with a cold glyph cache. Field paint spikes reached 128–148 ms. F8 keeps raster work off paint: visible primary/translation glyphs are rendered as QImage on a below-normal worker and installed into the existing high-DPI sprite cache one QPixmap per GUI tick. During the bounded cold gap, F8 reuses the existing plain-glyph emergency renderer rather than creating a new visual engine.
3. Bilingual candidate ranking was coverage-first even during a precise request. A slightly more complete ordinary LRC pair could therefore beat an available quality-3 QRC/KRC + translation pair. F8 treats quality-3 as a hard class boundary for precise requests; coverage ranks candidates only inside the highest timing-quality class. Fast/classic bilingual lookup remains coverage-first.

## Ownership

- Playback clocks, seek, player transport, parser semantics and provider identity rules are unchanged.
- H51/H57/H62/H70 visual preset owners remain unchanged.
- Sync Doctor storage/actions are unchanged; only its presentation is restored to expanded.
- Hidden H75 proxy controls remain alive as configuration authorities; only their obsolete row layouts are physically retired.
- No `QPainterPath` or `_hires_glyph_sprite` cache-miss rasterization is introduced in the F8 paint wrapper.
