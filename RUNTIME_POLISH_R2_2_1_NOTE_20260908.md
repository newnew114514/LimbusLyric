# Runtime Polish R2.2.1 — Compact Preview Restoration

This is a presentation-only correction on top of R2.2.

- Restores the mature H89/H95F4F3 page-local collapsible preview for Studio Appearance/Motion pages.
- The shell-level R2.2 sticky preview host is retired to zero height, so it cannot compress the settings workspace or section navigation rail.
- The compact `预览` disclosure remains at the top of the relevant page. It uses the existing persisted `h89_preview_open` preference; a clean config starts collapsed.
- Motion preview replays only while that compact preview is expanded.
- No preview renderer, lyric/player state, settings ownership, ControlPanel wrapper chain, or animation formula is replaced.

R2.2 runtime fixes (KuGou visual proof, bilingual anchor ownership, material atomicity, cover colour/backoff, region explanation and control ordering) remain unchanged.
