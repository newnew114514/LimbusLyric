# H69 Optical Continuity + Edge Wrap Stability

H69 addresses two field-visible discontinuities left after H68.

1. Blur material readiness is now progressive. The H62 mid stage is emitted immediately when ready instead of waiting for the max stage. When the full-song atlas has fused, H61 row atlases are prewarmed for a bounded future timeline window. A row atlas that finishes after an ultra-short lyric has already entered history/fading is adopted by that resident row and its blur build is requeued.
2. Visible blur progress has a per-row monotonic floor over the H68 deadline planner. Retargets, fallback paths, history→release handoff, or capacity state changes may slow future motion but cannot make a row visibly sharper again.
3. Horizontal wrap topology no longer includes per-frame shake offsets. Shake still affects the final glyph draw position, but only stable baseline/flow geometry decides whether a glyph wraps to the neighboring screen-width cycle. This removes edge threshold ping-pong without flattening the living-shake style.

No player clock, seek, provider, lyric-acquisition, packaging command, or non-blur exit authority is changed.
