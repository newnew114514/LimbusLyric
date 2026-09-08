# H95F10F10 — Render Plan + Resolved Visual Preset

This stage is an internal ownership consolidation, not a new visual effect.

- One frame contract now carries current primary/translation inputs, timing hints, next-line identity, cache route and plan build cost.
- A resolved visual preset snapshots the final user-facing entrance/exit profile, translation scale/gap, shake, audio emphasis, perspective/wrap and mature material signatures.
- The active translation layout is resolved once and reused during the same paint instead of each downstream helper re-resolving it.
- `paintEvent` remains a thin consumer wrapper. It does not raster glyphs, parse lyrics, query providers, resolve typography, or implement effect formulas.
- Player clocks, seek authority, provider search, H51 typography, H57 depth, H62/H69 blur and H70/H71 exit semantics are unchanged.

The design intentionally follows a shared-runtime principle: resolve semantics once, let renderers consume the resolved contract, and avoid parallel helpers that independently infer the same state.
