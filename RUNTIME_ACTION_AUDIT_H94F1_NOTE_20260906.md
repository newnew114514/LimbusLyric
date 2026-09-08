# H94F1 Runtime Action Audit Closure

Date: 2026-09-06

This stability-only patch closes three independently reproduced H93F2/H94 defects without changing lyric-provider or playback authority:

1. H42 frozen-build liveness negative backoff can only be read/written after `_player_liveness_confirmed is False`. An unconfirmed negative therefore cannot be counted repeatedly by H13 from one cached probe.
2. `QPoint` is imported from `PyQt5.QtCore`, restoring H88/H89 settings-section scroll/highlight actions that previously failed under swallowed `NameError`.
3. `wintypes` is imported globally from `ctypes`, restoring native cursor/process fallback paths when PyWin32 or higher-privilege process queries are unavailable.

A new canonical action-level gate, `installer/CHECK_RUNTIME_ACTION_AUDIT_H94F1_REPLAY.py`, executes extracted functions from the real main source rather than checking for markers only. It verifies H89 navigation animation, native Win32 cursor fallback, fresh-negative liveness confirmation, confirmed-dead backoff, positive restart evidence, and fresh-epoch cache isolation.

No Spotify lyric fallback, QQ/NetEase/Kugou lyric search, transport clock, workspace grip, theme, OBS, or rendering behavior is intentionally changed by H94F1.
