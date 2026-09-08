# SPOTIFY LYRIC FALLBACK H94 — 2026-09-06

## Scope

H94 changes lyric-content fallback only. Spotify playback remains the H13 strict Windows-local GSMTC implementation. No Spotify Web API or lyric provider may own seek, playback state, player identity, or clock authority.

## Why Spotify playback already worked

H13 already selected Spotify by source-affine Windows GSMTC (`spotify.exe`) and treats Spotify as a strict built-in. Desktop and Store-style source IDs are accepted only when the GSMTC SourceAppUserModelId contains the Spotify identity; if no matching session exists, the sync layer fails closed rather than borrowing the Windows global current session. The packaged build already includes the WinRT Media.Control dependency.

## Lyric fallback order

1. Existing selected provider plus the mature NetEase / QQ / KuGou cross-provider ladder.
2. Musixmatch documented `matcher.subtitle.get` when `LIMBUSLYRIC_MUSIXMATCH_API_KEY` is explicitly configured. Spotify documents Musixmatch as its licensed/synced lyric supplier.
3. Spotify Web Player `color-lyrics` as a best-effort experimental fallback. H94 obtains a Web Player token without scraping browser credential stores. Anonymous token is attempted first; an advanced user may explicitly supply `LIMBUSLYRIC_SPOTIFY_SP_DC` or `LIMBUSLYRIC_SPOTIFY_BEARER_TOKEN`. Secrets are memory-only in H94 and never logged.

Translation-only mode remains the existing three-provider path. Spotify fallback is invoked only when the complete timed lyric result is empty.

## Failure isolation

All H94 network calls have short connect/read timeouts, cancellation checks, no retry loop, and soft-fail semantics. A Spotify/Musixmatch outage, authentication change, rate limit, region restriction, or internal endpoint change cannot replace or block the existing three providers. No new Python dependency is added.

## Distribution note

Spotify's public Web API does not document a lyrics endpoint. `color-lyrics` is an internal Web Player endpoint and may change without notice. For a distributed/commercial build, the documented Musixmatch API path is the preferred route and its API terms/licensing must be reviewed.

## Portability / thread-safety hardening

- H94 is installed immediately after H81 and before H82+, so it remains a lyric-data layer rather than leaking network/search responsibilities into presentation-only H87-H93 layers.
- The selected-player duration witness is frozen on the Qt/UI result thread before the Spotify worker starts. The worker performs network and pure payload conversion only; it does not read QWidget state.
- Auto/manual/mode generations are captured and wired into the worker's cancellation hook. A track switch, a newer manual request, or a newer mode refresh retires the old Spotify fallback before it can publish a stale result.
- Duplicate terminal-empty callbacks for the same transaction are de-duplicated behind a lock, preventing multiple concurrent Spotify requests for one generation/key.
- H13 source affinity accepts both desktop-style `Spotify.exe` and Microsoft Store AUMIDs containing the Spotify identity, while continuing to reject unrelated GSMTC sessions. Spotify playback still fails closed when no source-affine session exists.
