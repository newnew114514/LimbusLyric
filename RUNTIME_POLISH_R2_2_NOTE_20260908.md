# Runtime Polish R2.2 — 2026-09-08

R2.2 is a narrow runtime/UX polish pass on top of R2.1. It does not consolidate or remove the historical frontend wrapper chains.

Changes are limited to five field-log-backed areas:

- KuGou large-drift visual rail recovery now requires four coherent observations across at least 1.8s and near-wall-clock progression before authority can be regained.
- The bilingual translation lane keeps its own reveal/alpha but uses the primary row as its spatial anchor; it no longer adds an independent entrance offset/shake path.
- Cold material fallback is coherent by row/lane instead of mixing decorated/plain glyphs inside one visible subtitle. History plain fallback is also drawn as a row unit.
- Cover-follow applies persisted colour immediately, honours the existing artwork negative-cache/backoff, and drops stale cover workers after rapid track changes.
- Studio appearance UX is reordered to Layout → Subtitle Range → Preset → Font/Outline → Light/Material; Studio preview is kept visible while editing, the subtitle range gets a live screen diagram, and the overlapping center-frequency user control is retired at neutral 100%. Legacy page-local preview behaviour is preserved.

No player-specific seek formula, lyric timing formula, exit-effect formula, or wrapper consolidation is introduced by R2.2.
