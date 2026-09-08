# H95 · Unified Lyric Foundation + Sync Doctor V1

H95 intentionally adds a sidecar model and a display-only timing correction layer without replacing the mature provider/search/transport path.

## Unified Lyric shadow model

The accepted lyric payload is still parsed and rendered by the existing `parse_lrc()` / `LyricWindow` path. H95 separately mirrors that same parser output into a versioned dictionary model:

- Track: identity, song, artist, source.
- Lines: start/end, text, role, translation, romanization.
- Words: precise provider token text plus start/end and character slice.

H95 does not invent translation, romanization, duet or background roles. Those fields remain empty/`MAIN` until later formats such as TTML provide real evidence. The shadow model has zero playback, seek or provider authority.

## Sync Doctor V1

Sync Doctor stores corrections per exact normalized `song|artist` identity in the existing atomic user config. It never rewrites QRC/LRC/provider lyrics or player position.

- ±50/±100 ms buttons add a manual display-only adjustment.
- “这句现在才该出现” records `(base display clock, source line timestamp)` as an anchor.
- Zero or one anchor uses translation-only correction.
- Two or more anchors spanning at least 15 seconds may fit `source_time = scale * base_display_time + intercept`.
- Linear scale is accepted only inside 0.98–1.02; unsafe fits fall back to a fixed offset.
- Final per-song correction is always clamped to ±5000 ms.
- At most eight anchors are retained; re-anchoring approximately the same source line replaces the old evidence.
- “清除本曲修正” removes only the H95 sidecar data and restores the pre-H95 display clock.

The correction is applied after the pre-H95 `LyricWindow._playback_position()` result. Existing QQ/NetEase/KuGou/Spotify clock, seek, render-phase and provider offsets therefore remain the upstream authority.

## Release gate

`CHECK_UNIFIED_LYRIC_SYNC_DOCTOR_H95_REPLAY.py` executes the correction fitter and unified timeline adapter and also asserts H95 does not replace provider/search/transport/parser ownership.
