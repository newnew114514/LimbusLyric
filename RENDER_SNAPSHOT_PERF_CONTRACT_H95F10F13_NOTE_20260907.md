# H95F10F13 — Render Snapshot + Performance Contract

- Adds a small, stable RenderPlan snapshot for replay/regression comparison.
- Captures lyric ownership/quality/timing, visual preset choices, route, plan cost and prefetch queue depth.
- Tracks cold-frame and unified-track ratios without adding a periodic logger.
- Declares paint hot-path invariants: no provider, raster, typography resolve, image filtering or local effect formulas.
- Does not change renderer, clock, search, seek or user effect formulas.
