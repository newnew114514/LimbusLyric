# H87 — Premium Interaction + Dynamic Record + Frontend Palettes

H87 is presentation-only. It does not take player clock, seek, provider, lyric-search, or subtitle lifecycle authority.

## Changes

- Page navigation uses a bounded two-surface shared-axis snapshot transition. The navigation strip remains live; only the workspace content is frozen for the transition, avoiding dense-widget re-composition.
- The Listening Room record now uses cached current-track artwork. Artwork cross-fades on track changes and rotates only while the existing media state reports `playing`; pause/stopped freezes the record.
- Cover images are fetched on a daemon worker and cached under the user config area for 90 days. QPixmap creation/application remains on the Qt/UI side.
- A thin Hero progress rail reuses the existing `MediaSessionSync.snapshot()` values for presentation only. It does not create a new clock or poller.
- The top-right **界面** popup now owns a persistent frontend selector: **Lyric Studio · 深林** and **Classic · 玫瑰暗色**. Both preserve the same widgets, config owners, player logic and desktop lyric rendering.
- The Codex Studio tail is hardened to use the canonical Qt imports and optional activation guards so historical replay isolation does not import a later presentation layer unexpectedly.

## Interaction policy

- One page-transition owner only; H80's old per-page micro reveal is not stacked with H87.
- Record motion is ~30 fps and only active while playing or during a short artwork cross-fade.
- No continuous decorative page animation.
- Network artwork work never runs on the GUI thread.
