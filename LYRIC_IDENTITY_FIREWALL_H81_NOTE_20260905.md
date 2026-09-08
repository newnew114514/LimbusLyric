# H81 LYRIC IDENTITY FIREWALL — 2026-09-05

## Why this patch exists

Field logs for `熱異常 (feat. 足立レイ)` proved an authority inversion: QQ UIA reported the real 03:59 / 239000ms transport, while a cross-version lyric cache/result carried 203000ms. The lyric duration was allowed to complete MediaSync duration, so the real player duration was rejected and subsequent seek positions were ignored by the lyric clock. The resulting QQ `qq-track-switch-hint` could then carry the poisoned epoch into the next song.

## H81 changes (narrow outer compatibility layer)

- Purges non-instrumental QQ/KuGou cache entries whose version key has no duration, plus positive-duration rows whose stored payload duration conflicts with the key. User-owned/custom rows are untouched.
- Downgrades QQ pre-bind `qq-track-switch-hint` from hard new-song duration to transition evidence. The post-bind resolver must corroborate it; the same pre-bind duration cannot cross into the new title without independent current-title player evidence.
- If selected QQ has no player-owned duration yet, a lyric body may display but its candidate duration is set to zero before the historical auto-result handler. This prevents lyrics from setting transport/seek scale.
- Fast-stage rows are covered too: if the visible row publishes `duration=0` but keeps a provider candidate in `lyric_candidate_duration_ms`, H81 quarantines that candidate for later player-duration reconciliation instead of letting a failed precision upgrade hide the conflict.
- Once direct QQ GSMTC or mature validated QQ UIA supplies the selected-player duration, H81 either authorizes a matching lyric duration for presentation or schedules a duration-anchored version refetch on conflict. No `bind_track()` call is used for the late authorization path.
- Applies the same zero-witness boundary to Spotify cross-provider lyrics. Existing H13 Spotify GSMTC duration remains the trusted witness.
- Separates lyric source from playback source at the outer search boundary. A NetEase lyric source cannot lend Bridge track ID/duration to Spotify/QQ/KuGou playback, and a QQ lyric source cannot invoke QQ transport duration resolution while another player owns playback. Provider words remain available; foreign transport identity is stripped.
- Reuses existing KuGou H38 and NetEase H38 selected-player duration witnesses where available, without changing their clock or seek implementations.

## Audited but intentionally not redesigned

- KuGou already has H28 zero-duration cache withdrawal and H38/H41 player-owned duration/seek authorization. H81 leaves those clock/seek methods unchanged.
- NetEase already has H38/H41 native player duration, identity veto and version-reconcile logic. H81 leaves those clock/seek methods unchanged because another rewrite would be higher risk than the evidence supports.
- QQ Software-2 source-locked `_merge_uia_position`, `bind_track`, `AsyncPlayerUiPositionReader.poll`, and original `_request_auto_track` bodies are unchanged. H81 wraps only ControlPanel lyric/identity boundaries.
- Manual/custom lyric ownership, UI renderer, blur lifecycle, network provider implementation, dependencies, PyInstaller spec, Inno Setup script, and `BUILD_RELEASE.cmd` packaging command are unchanged.

## Regression scenarios now gated

The dedicated replay covers the observed 203000ms unknown-duration QQ lyric result against a validated 239000ms player witness; the fast-stage hidden-candidate case; QQ pre-bind track-switch-hint contamination; cross-player NetEase/QQ transport leakage; and Spotify cross-provider zero-witness handling. It also hashes the H80 source-locked player-clock bodies and requires them to remain byte-identical at function-body level.

Canonical release suite after H81: **143 gates**.
