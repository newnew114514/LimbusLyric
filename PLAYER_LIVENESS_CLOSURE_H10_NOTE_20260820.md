# H10 Player-Liveness Closure

## Field trigger
A real H8F2 log showed QQMusic disappearing while the selected-player state continued to advance the old lyric timeline. After the QQ process/session disappeared, LimbusLyric kept publishing `source=qqmusic` lyric rows until the user manually pressed Stop. A second restart log showed QQ UIA `hwnds=0` and no QQ clock while the app remained armed against an unrelated PotPlayer GSMTC session.

## Runtime authority
H10 adds a process-liveness authority above every presentation and transport fallback for the three built-in players.

- Liveness uses Toolhelp32 process enumeration on a dedicated daemon worker, never from Qt/snapshot and never through `tasklist`/`OpenProcess`.
- Missing process must be observed three consecutive times. A single GSMTC disappearance, hidden/minimized window, or one failed probe cannot retire playback.
- Confirmed process death hard-retires generic auto-local, H9 UNKNOWN carry, QQ loop-local/clock authority, KuGou rail-local/GSMTC authority, UIA/seek anchors, and NetEase Bridge/native primary state.
- Public MediaSync becomes `stopped`, disconnected, with no position. Old identity/transport epochs are invalidated so stale samples cannot revive the dead track.
- ControlPanel stops the visible lyric and cancels in-flight auto-track jobs, but LimbusLyric remains armed-idle; the application itself does not exit.
- When the same player reopens, cached lyrics are restored only after a real `playing`/`paused` state with a real position is observed. Reattachment is marked startup-existing so no fake song-zero clock is created.
- If the reopened player is on another track, the normal auto-track transaction fetches/binds that identity instead of restoring the old lyric.

## Cross-player scope
The same liveness authority covers QQMusic, CloudMusic and KuGou (`kgmusic.exe`/`KuGou.exe`). KuGou's H7 transport/pause authority and H9's display-only UNKNOWN carry remain unchanged while the process is alive.

## Release gate
`installer/CHECK_PLAYER_LIVENESS_CLOSURE_REPLAY.py` proves process enumeration isolation, three-sample death confirmation, hard clock retirement, armed-idle UI behavior, real-position reopen restore, and H9 compatibility.
