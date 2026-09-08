# H39 Win10 KuGou Authorized Seek + COM Lifetime Closure

Field log `20260831-100359` showed two remaining Win10-only defects after H38:

1. H38 correctly logged `seek-scale=disabled` for KuGou when only KRC/lyric duration was known, but H37's narrow-band mouse consumer still read `_uia_duration_ms` / state duration and committed rail clicks with that unowned scale. H39 moves the final authority check to `_kugou_target_from_cursor` and `_kugou_commit_gesture_seek`: on Win10 frozen, only `_h38_kugou_owned_duration()` may scale a rail gesture. If unavailable, the physical player click is allowed to reach KuGou but LimbusLyric publishes no guessed target; it records the gesture epoch/ratio and waits for H38 player-side evidence.

2. A `0x8001010d` trace still occurred during `app.exec()` before lyric playback had entered H35's playback-scoped cyclic-GC guard. H39 disables automatic cyclic GC for the whole Win10 frozen process before the Qt event loop starts. CPython reference counting remains active. Win11 and non-frozen/source runs are unchanged. `LIMBUSLYRIC_WIN10_PROCESS_GC_GUARD=0` is an explicit opt-out.

NetEase native timing is unchanged. H39 only refreshes H38's accepted payload duration/key after a successful current NetEase result, preventing stale KuGou payload metadata from re-triggering the same duration reconciliation.

Win11 transport/clock logic is intentionally unchanged.
