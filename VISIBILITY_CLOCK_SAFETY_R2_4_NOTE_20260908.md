# LimbusLyric R2.4 — Cross-player visible-lyric clock safety

This patch is driven by field logs where lyrics were successfully fetched and parsed, yet the renderer had no publishable playback position and therefore produced no visible subtitle row.

## Root regression

`_zero_touch_first_attach_pending` described a **track attachment transaction**, but before R2.4 it was cleared only in one final lyric-result bind branch. R2.1's progressive fast stage can accept and display a lyric payload without entering that branch. The flag could therefore remain true after the first track and leak into later tracks.

That leak is provider-sensitive because the fast-stage shortcut is selected by lyric source (`QQ音乐` / `酷狗`), while the leaked flag is player-global. The result is cross-player risk, not a KuGou-only bug.

R2.4 consumes the flag immediately after the first confirmed provisional track bind. `MediaSessionSync._startup_existing_attach` remains independent and continues protecting the actual pre-existing first song until a real position witness appears.

## Player matrix

- **KuGou** — confirmed field failure. A leaked startup attach suppresses the local rail seed on later tracks, leaving `fresh_position=None` / `kugou-waiting-real-clock` even when LRC/KRC is ready. R2.4 restores normal provisional display clocks for later tracks and resets only Host-V2's negative-cache gate when a loaded lyric remains positionless.
- **QQ Music** — same first-attach lifecycle risk. Later tracks must use the existing display-only auto-local lane while compact-pair/GSMTC authority converges. The real pre-existing first track still waits for a trustworthy player witness.
- **NetEase Cloud Music** — the generic lifecycle risk exists. In addition, the old generic auto-local path could publish a synthetic zero for a true startup-existing track; R2.4 forbids that for every player. NetEase keeps native-log/Internal-Bridge first, with its existing safe UIA fallback.
- **Spotify** — the lifecycle risk exists. R2.4 also forbids synthetic zero on the actual pre-existing first track. Spotify currently has no player-specific second position adapter beyond its local GSMTC contract, so if Windows publishes metadata/playback but no usable timeline on that one initial late attach, exact current position is not knowable without adding a new Spotify-specific adapter. Later confirmed track changes may use the display-only local clock normally.

## Visibility contract

Old `H34酷狗切歌自动弹幕显示已确认` only proved that the overlay widget was visible and a lyric timeline existed. It could be followed immediately by `visual_count=0`.

R2.4 renames that event to **container ready** and introduces two actual end-to-end signals:

- `R2.4歌词已就绪但尚无可见字幕 ... visual_count=0 | success=0`
- `R2.4首条弹幕真正可见 ... visual_count>=1 | success=1`

A loaded timeline with `position=None` is now treated as an observable liveness failure. After 650 ms the renderer requests the selected player's existing asynchronous evidence path; it does not perform accessibility scanning on the paint thread and does not grant seek/formal clock authority.

## Non-goals

- No wrapper-chain consolidation.
- No renderer/effect formula redesign.
- No provider identity relaxation.
- No fabricated mid-song position when a player exposes no timing evidence.
