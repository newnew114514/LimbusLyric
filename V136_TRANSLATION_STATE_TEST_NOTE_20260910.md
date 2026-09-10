# v1.8.9.136 translation-state test build

This is a test-only successor to the published v1.8.9.135 baseline. It is intended for endpoint validation before any release or merge to `main`.

## Field failures addressed

1. Persistent translation-only mode can have no payload for track A. Pressing Start while that semantic presentation block is active must preserve the user's running/auto-track intent; a later valid payload for track B must appear without a second Start click.
2. Repeated Start on an already-running, already-bound lyric performance must be idempotent. It must not rebuild the H95 lyric shadow/translation sidecar or restart MediaSync, which field testing associated with disappearing bilingual translations and random phase drift after repeated clicks.
3. A mode-refetch must not combine a cached old loaded identity with a newer player duration. If the live player has advanced beyond the loaded payload, the old mode-refetch is abandoned and the current track re-enters the existing auto-track ownership path under the new mode.

## Deliberately unchanged

Provider parsers/search scoring, QQ/NetEase/KuGou clock algorithms, seek logic, rendering formulas, cover matching, packaging architecture, installer AppId/install location, and the v1.8.9.135 ownership hotfix are not redesigned by this test patch.

## Friend test sequence

- Translation-only: play a song with no translation, keep the mode enabled, press Start if needed, then switch directly to a song that has a translation. The second song should appear automatically without toggling the mode or pressing Start again.
- Stale mode-refetch: while a translation-only miss has left the old payload cached, switch to a new song and then switch back to original/bilingual mode. Logs must not show the old title searched using the new song's duration.
- Repeated Start: with bilingual original+translation visibly working, press Start repeatedly 5-10 times. Translation must remain visible and the timing must not drift merely because Start was clicked repeatedly.

This branch is not a release candidate until those endpoint sequences pass on real Windows players.
