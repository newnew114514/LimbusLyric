# Runtime UX + Core R2.3 — 2026-09-08

This build continues from R2.2.1. It does **not** consolidate or reorder the historical runtime monkey-patch chains.

## Field UX fixes

- Studio preview is controlled by a compact button next to the workspace title on the Subtitle/Motion pages.
- Folded preview has zero shell height; when opened it is a fixed 142px stage above the scrolling settings so it stays visible while the user scrolls.
- The previous page-local preview rail is retired for Studio only; Legacy keeps its existing H95F4F3 path.
- The large subtitle-region explainer is removed from vertical layout. A 118x48 inline screen map now sits beside the region controls.
- Standalone `样式预设` card is retired. Its real preset controls are moved into `字体与轮廓` without replacing config owners.
- Subtitle page frequent-first order: `字体与轮廓 → 光与材质 → 基础表现 → 排版与布局 → 字幕可出现范围`.
- The retired center-frequency control stays neutral at 100%; region bounds remain the user-facing placement control.

## External-player / lyric architecture ideas adopted without copying another project

- `PlaybackSnapshot` now exposes monotonic `position_at()` / `sampled_dict()` semantics: a trusted sample carries its sampling time and can be extrapolated locally while playing.
- `PlaybackCapabilities` is a provider-neutral observed-capability contract. It reports what evidence is present (GSMTC/UIA/holdover/visual rail/gesture) but never chooses transport authority.
- `MediaSessionSync.sampled_snapshot()` and `.capability_snapshot()` publish these contracts additively; mature QQ/KuGou/NetEase clock/seek wrappers are unchanged.
- Unified lyric lines now contain derived `render_hints`; H95F10F12 reuses them instead of re-deriving visual handoff/end semantics in every consumer.
- `active_line_window()` provides one pure helper for current/history/upcoming lyric slices, matching the shared-runtime principle already used by the H95F10F9/F10/F11/F14 render plan/prefetch pipeline.

## Explicit non-goals

- No new provider HTTP implementation.
- No change to QQ/KuGou/NetEase transport authority or seek formulas.
- No renderer effect formula changes.
- No frontend wrapper consolidation.
