# OUTPUT / DIY / SPOTIFY H13 — 2026-08-26

H13 is an outer extension on the frozen H12/H11 candidate. It does not redesign QQ Software-2, KuGou golden transport, or NetEase native authority.

## Delivered

- **Per-song lyric content slots:** every exact song+artist identity can own three independent user payloads: `precise`, `classic`, `translation`. A saved user payload bypasses provider network fetch in automatic, manual, and semantic mode-switch paths. Deleting the active slot restores automatic provider lyrics.
- **OBS output:** `LimbusLyric OBS Lyrics` is a presentation-only transparent mirror. It owns no `MediaSessionSync`; it copies only the current lyric visual region at a bounded 20fps and inherits the main lyric opacity. The main overlay and the OBS window remain separate capture targets.
- **Spotify:** fourth built-in player using strict Windows local GSMTC only. No Spotify Web API, OAuth, client secret, refresh token, or account transport is introduced. Identity and timeline are accepted only from a source-affine Spotify media session plus bounded local process liveness. Spotify window titles are never canonical track identity.

## Audit closures before release

- H13 runtime closures must be defined **before** the `if __name__ == "__main__":` startup block. An earlier work snapshot placed them after `sys.exit(app.exec_())`, which would have made the features present in source but inactive at real runtime; the H13 gate now locks ordering.
- User lyric payload matching is stricter than visual-style matching: runtime slots require exact normalized song **and artist**, so artist-less/same-title style aliases cannot apply another song's lyrics.
- Spotify's own source-affine GSMTC duration is the lyric-version witness for QQ/NetEase/KuGou lyric providers in auto, manual, and mode-switch paths. A lyric source never becomes Spotify playback authority.
- Controls created by H13 are registered into the H12 immutable UI-scale baseline, so 100/110/125/150% scaling remains consistent.
- Historical DIY selection cannot copy the currently playing lyric into another song identity.
- Historical automatic-lyric preview is generation-scoped and cooperatively cancelled after the 18s UI budget; stale provider work cannot publish into a newer editor transaction.
- OBS capture uses the source window's bounded current visual region rather than grabbing a full-screen transparent surface every frame.

## Intentionally not delivered

- Automatic in-place EXE replacement remains deferred. H12 HTTPS check + user-confirmed download/open remains the update model.
- Spotify remains Windows-local-GSMTC only; environments where Spotify publishes no usable GSMTC timeline fail closed instead of falling back to window-title/UIA guessing.
- Spotify does not receive a fourth per-player visual-style slot in the mature ALL/QQ/NetEase/KuGou style schema; it uses ALL/global presentation style. The new three lyric-content slots work with Spotify because they are track-owned, not provider-style-owned.

## Release contract

- Canonical suite: **71 gates**, including `installer/CHECK_OUTPUT_DIY_SPOTIFY_H13_REPLAY.py`.
- H12/H11 gates remain mandatory.
- `CHECK_LEGACY_BASELINE_INTEGRITY.py`: 481 unchanged old functions.
- `CHECK_KUGOU_GOLDEN_BASELINE.py`: 22 source-locked KuGou methods.
- Do not update locks/allow-lists to hide an unreviewed regression.

## Environment limitation

This environment can source-audit and replay/fault-test the code, but cannot truthfully claim a Windows Spotify/OBS/PyQt real-machine run. Real Windows logs remain higher-value evidence for environment-specific behavior.
