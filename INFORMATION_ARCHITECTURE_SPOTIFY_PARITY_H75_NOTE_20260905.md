# H75 — Information Architecture + Spotify Parity (2026-09-05)

H75 is the third-stage front-end closure built on the H72 runtime checkpoint, H73 editorial shell and H74 preview/inspector layer. It changes product organization and two missing Spotify user-level parity contracts; it does **not** take playback/seek/provider authority.

## Product organization

- Motion is visual-only. The historical player offset row is hidden there and represented in **Settings → 同步与输出**.
- 同步与输出 exposes independent NetEase / QQ / KuGou / Spotify display offsets and the mature 普通 Overlay / OBS 独立输出 / 捕获排除 mode through proxies to existing controls.
- The historical H12 “显示与更新” mixed card is retired from product view. H74 already re-homed font weight/opacity/cover-follow and H70 re-homed exits; H75 re-homes UI scale, output mode and updater while leaving H12 controls/config keys as compatibility owners.
- The raw HTTPS update endpoint is no longer a normal form row. It remains discoverable under the Update overflow action “自定义更新源…”.
- Settings card names are semantic: 应用界面 / 同步与输出 / 空间与画面 / 应用行为 / 界面背景 / 桌面与响应 / 更新.

## Global search

The header search is now a global search across all five first-level pages. The query survives page navigation; if the current page has no hit, H75 moves to the first matching page. Hidden compatibility cards are excluded from search results. No command palette, background indexer or new thread is introduced.

## Spotify parity

- New `spotify_sync_offset` is persisted independently. Spotify no longer falls through to the NetEase display offset.
- Per-song DIY has a first-class `spotify` rule slot beside `qq`, `netease`, and `kugou`. Schema v5 normalization now preserves that slot; switching ALL ↔ per-player seeds/preserves all four slots.
- Runtime song-style selection recognizes `Spotify` / `spotify.exe` and consumes `rules.spotify` when the song is in per-player mode.

## Compatibility and ownership

- Existing QQ / NetEase / KuGou offsets keep their original controls/config keys. H75 uses proxy controls in the new semantic surface.
- Existing `h12_capture_combo`, `h12_scale_combo`, update check/download/status objects remain the mature behavior owners.
- Existing tab indices remain 0..4; H73 visual navigation order is unchanged.
- No MediaSessionSync, seek state machine, lyric provider search, desktop FadingLine/history lifecycle, raster worker or packaging dependency is added or replaced.
- H75 has **no playback/seek/provider authority**.
