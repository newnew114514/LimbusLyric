# RC late-attach player-scope closure — 2026-08-17

## Confirmed field failure

The supplied Windows log showed this sequence:

- KuGou zero-touch armed with `first_attach=1` and loaded a KuGou track.
- The user switched to QQ; QQ armed with `first_attach=0` solely because a KuGou `_loaded_track_key` already existed.
- The user later switched back to KuGou; the provisional bind entered `lazy-zero-bootstrap` / `auto-track-bootstrap` instead of waiting for a player position witness.

That contradicted the candidate contract that a background-existing track must not turn detection latency into song position zero.

## Root cause

`ControlPanel._arm_zero_touch_selected_player()` treated any non-empty `_loaded_track_key` as proof that the newly selected player was already attached. `ControlPanel._request_auto_track()` repeated the same global check.

The project already records the independent actual player in `_loaded_player`; the late-attach lifecycle was not using it.

## Minimal closure

- First-attach pending is true when no track is loaded **or** the cached track belongs to a different actual player.
- The request path requires the pending transaction to belong to the currently selected player, then passes the existing `startup_existing` flag unchanged.
- Same-player ordinary track changes retain their existing detection-latency/provisional behavior.

No player adapter or authority function was modified.

## Deterministic replay

`installer/CHECK_ALL_PLAYER_LATE_ATTACH_PLAYER_SCOPE_REPLAY.py` executes the real control methods with bounded fakes and verifies:

- fresh launch;
- QQ-loaded → KuGou-selected with NetEase lyric source;
- KuGou-loaded → QQ-selected with NetEase lyric source;
- NetEase-loaded → KuGou-selected with QQ lyric source;
- same-player ordinary transition as a negative control.

Cross-player cases must bind with `startup_existing=True` and `initial_position_ms=0`. The same-player control must remain non-late-attach and preserve its historical detection-latency seed.
