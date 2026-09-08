# LimbusLyric UX EXTENSIONS H12 — 2026-08-26

H12 is a presentation/control-panel extension on top of the frozen H11 post-release responsiveness baseline. It deliberately does **not** redesign QQ / NetEase / KuGou playback-time, seek, identity, or lyric-provider authority.

## Added in H12

- Control-panel UI scale: 100% / 110% / 125% / 150%. Font sizes, stylesheet spacing/padding, layout spacing/margins, and explicit child-control bounds scale from immutable baselines. The main window minimum size is not forcibly enlarged.
- Subtitle opacity: 0–100%, live through the lyric top-level window opacity.
- Global font weight: Qt weight 1–99 with readable labels. The old bold checkbox remains a regular/bold shortcut; per-song DIY bold remains higher priority.
- Shake redesign: bounded irregular micro-jolts with rapid exponential decay, no new rotation/scale, hard displacement cap 3.5px.
- Cover-follow text color: opt-in strict title/artist NetEase cover lookup on a daemon worker, representative-color extraction with saturation/value correction, track ownership guard, and graceful fallback. Explicit per-song DIY/random text color remains higher priority. Manual color selection returns to custom mode; cancelling the picker does not.
- Exit effects separated from entrance effects: full-line fade, per-character disappearance, left-to-right wipe, right-to-left wipe, quick shrink/fade, instant. Wipes reuse cached glyph advances and do not rebuild glyph paths every frame.
- Lyric-window capture mode: Normal Overlay / Capture Exclusion. Capture exclusion is attempted only on Windows 10 2004+ (build 19041+) and uses `WDA_EXCLUDEFROMCAPTURE`; older Windows is rejected before the API call so it cannot silently degrade to legacy `WDA_MONITOR` behavior.
- Update check: configurable HTTPS GitHub Release/JSON endpoint (or `LIMBUSLYRIC_UPDATE_URL`), single-flight background request, current/remote version comparison including H-stage suffixes, release notes, and a user-controlled Download Update button. Returned page/download URLs are HTTPS-filtered. H12 never self-overwrites the running EXE.

## Explicitly deferred

- Dedicated OBS mirror output window: requires a second presentation target sharing lyric state without duplicating MediaSync/timeline state.
- Spotify as a fourth player: requires a separately reviewed identity/status/position/seek authority adapter.
- Three independent per-song lyric payload slots (precise/classic/translation): requires song-style/cache schema and ownership migration, not a small UI-only change.
- Automatic in-place updater: first release remains check + user confirmation + external HTTPS download/open.

## Review invariants

- 481 legacy locked functions and 22 KuGou golden methods remain source-identical.
- H11 GUI responsiveness/liveness/ownership/shutdown closures remain active.
- Cover/update networking is daemon/background work and cannot become playback authority.
- UI scale is reversible from captured unscaled baselines; no cumulative scale-on-scale application.
- Capture exclusion never uses `WDA_MONITOR` fallback.
- Dedicated gate: `installer/CHECK_UX_EXTENSIONS_H12_REPLAY.py`.

## Validation boundary

The release gates and source audits can run in the current Linux container, but PyQt5 is not installed in this container, so a real QWidget/Windows capture runtime test cannot be claimed here. Windows + PyQt + real-player verification remains the final host-side step.
