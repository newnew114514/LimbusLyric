# LimbusLyric v1.8.9.135 translation-only ownership hotfix

## Field symptom

When the persistent **translation-only** mode is enabled, a track whose translation search fails can leave the automatic presentation suspension/failed-track ownership state active. If the next track successfully resolves a translation payload, the legacy result path loads that payload and calls `_launch_current_lyrics()` before the old failed ownership state is cleared. The H11 presentation guard therefore treats the successful new payload as stale and keeps the overlay blank until the user toggles lyric mode.

## Fix

For a generation/key/source/mode-confirmed successful automatic lyric transaction, v1.8.9.135 releases the semantic mode block **and** the old automatic suspension/failed-key barrier before entering the legacy apply/launch path. The previous ownership state is snapshotted and restored only if the legacy handler fails to bind the returned payload to the current track.

This preserves the existing protection against reviving an old song's lyrics after a genuine new-track search failure while allowing a later successful track to take presentation ownership immediately.

## Scope

- No player clock, seek, timing, render, or identity formulas are changed.
- R9.2 QQ modern search routing is retained.
- R9.2 trusted NetEase song-ID cover direct-fetch routing is retained.
- Runtime/UI/updater/installer version metadata advances to `v1.8.9.135`.

## CI note

Windows CI checkout line endings are pinned through `.gitattributes` so the source-lock and hotfix patcher see the same normalized source bytes as the repository.
