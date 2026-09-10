# LimbusLyric v1.8.9.136 field regression closure

## Evidence

The 2026-09-10 Windows field logs identified two narrow state-lifetime regressions worth fixing without changing player clock, seek, renderer, or provider parsing formulas.

1. **Bilingual translation can disappear after Start / Restart / relaunch.** A valid H95F5 translation sidecar may already be fetched and cached, but `_launch_current_lyrics()` rebuilds the H95 unified main-lyric model. The cached translation is not guaranteed to be reattached afterward. Toggling the bilingual mode off/on causes the translation to reappear because that path reapplies the sidecar.
2. **Mode refetch can mix a stale loaded song with a newer player identity/duration during a fast track handoff.** The field log shows a mode-refetch for `simple times` using the already-new `244000ms` QQ duration, immediately followed by the correct current identity `呼吸 / 林忆莲`. Provider duration validation then rejects all three providers for the stale song.

## v1.8.9.136 changes

- Wrap the final `_launch_current_lyrics()` path and, after a successful relaunch, reattach only an already-cached H95F5 bilingual translation through the existing H95F10 provider/duration/identity validation. Original-only mode is unchanged and no new provider request is forced.
- Wrap the final semantic mode-refetch path and veto it when the loaded lyric identity disagrees with the bound MediaSync track or a detected current player track. The user's selected lyric mode is preserved; the current/new-track automatic transaction remains authoritative.
- Retain the v1.8.9.135 translation-ownership hotfix and R9.2 QQ modern search / trusted NetEase-ID cover routing.

## Explicitly not changed

The reported roughly tens-to-100ms variation after repeated Restart is **not patched in this build**. The field logs keep `user_offset=0ms` and do not yet prove a persistent clock-offset mutation. Changing the mature player clock/PLL/seek path without stronger evidence would have a higher regression risk.

No player clock, seek, transport authority, lyric provider parser, translation alignment algorithm, render formula, or effect formula is changed by the V136 layer.

## Validation order

1. Dedicated `tools/V136_FIELD_REGRESSION.py` must fail on the old behavior and pass with the V136 layer.
2. Existing H49/H50 ownership and H95F9 translation regressions are rerun.
3. Source lock and packaging structure are checked.
4. PyInstaller frozen application is built and packaging smoke is run.
5. Inno Setup produces the v1.8.9.136 test installer and SHA-256 file.
6. Full canonical release-gate audit remains a later release gate after field testing; this test build is not automatically published as `Latest`.
