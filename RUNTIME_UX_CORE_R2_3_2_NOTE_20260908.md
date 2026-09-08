# Runtime UX + Core R2.3.2 audit hotfix — 2026-09-08

Scope is deliberately small: preview visibility + audit closure. No player clock, seek, lyric search, renderer effect formula, or historical wrapper topology is changed.

## Fixed after static audit

- Added a visible frame around the expanded Studio preview host. Folded preview remains zero-height.
- Unified the title preview toggle with the existing H89 `h89_preview_open` state owner. The short-lived `r23_title_preview_open` key is migration-only and is retired on save.
- After moving the Style Preset controls into Font & Outline, the now-empty standalone preset card is physically removed from the page layout. This prevents the H89 section rail from recreating a dead `样式预设` navigation target.
- Removed two unused main-module imports (`active_line_window`, `build_line_render_hints`). The helpers remain available in `limbus_core` as staged APIs.

## Audit finding that is not being hidden

`MediaSessionSync.sampled_snapshot()` and `capability_snapshot()` are currently published additive contracts. They do **not** yet own player authority or materially change playback behavior. Likewise `active_line_window()` exists in the core model but is not yet a production scheduling owner. They should not be counted as completed performance/compatibility gains until a later, separately tested consumer is introduced.

This is intentional: wiring them into mature QQ/KuGou clocks or renderer scheduling without field evidence would create more risk than benefit.
