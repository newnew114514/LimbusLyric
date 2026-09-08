# H95F7 · Render Hotpath + UI Coherence

Windows field telemetry on 2026-09-07 showed a 59 Hz / 1920×1080 desktop reaching roughly 52.7 ms average subtitle paint time, 87.1 ms p95 paint, 80.6 ms average frame interval and 141 ms max frame interval while only three live visuals plus two history rows were present. Provider-side stalls remained around 0.2 ms. The regression was therefore in presentation CPU work rather than lyric-provider or playback-clock authority.

## Render hotpath

H95F6 correctly made translation a second visual lane, but rebuilt `QPainterPath.addText()` glyph paths plus outline/shadow/glow on every paint. H95F7 keeps the same dual-lane semantics while routing translation through the existing worker-built whole-song fragment atlas. Translation characters are added only to a secondary-style atlas key. Until that atlas is ready, the lane uses the mature LRU high-DPI glyph sprite cache, so vector construction is a cache miss rather than a per-frame operation. Active translation uses one `drawPixmapFragments()` batch when an atlas is available; history/exit translation does the same and preserves per-character/wipe opacity state.

The H95F5 and H95F6 secondary paint passes are suppressed during the mature primary paint and H95F7 draws the translation lane once. Primary precise timing, seek ownership, player clock and provider search are unchanged.

## Dirty-region / clipped-corner closure

H95F5 used a broad placement group box for bilingual dirty ownership. H95F7 restores the mature primary dirty-region calculation and unions a translation-specific mapped region with an explicit anti-alias/glow/stroke edge guard. This avoids both under-paint clipping at rotated/perspective glyph edges and unnecessarily repainting the whole bilingual group rectangle.

## Background CPU backoff

A confirmed-dead selected player previously continued the full liveness probe cadence. H95F7 preserves liveness semantics but changes scheduling only: unknown uses the historical full cadence; confirmed alive uses a cheap positive probe every 1.5 s and performs a full probe when the fast proof disappears; confirmed dead uses positive-only launch detection every 1.5 s and full negative verification every 10 s. No playback/seek/clock method is changed.

## Settings coherence

- `仅显示翻译（替换原歌词）` and `原歌词 + 翻译（双语）` remain mutually exclusive but neither disables the other. Clicking either mode can switch directly from the other.
- The bilingual controls are relocated directly after the real `trans_check` row rather than depending on shallow page-layout assumptions.
- H75's four retired offset layout-items are removed from the visible `同步与输出` VBox, eliminating blank height. The authoritative hidden player values remain alive. The obsolete H95 divider line is removed; current-player offset, global output and Sync Doctor remain visible.
- Modern title glass uses alpha 158 (Classic) / 152 (Studio), while Legacy chrome remains independently scoped.

## Ownership

H95F7 is a rendering/scheduling/UI-coherence layer. It does not replace `parse_lrc`, lyric provider search, media position/seek authority, precise lyric timing or H95 correction math.
