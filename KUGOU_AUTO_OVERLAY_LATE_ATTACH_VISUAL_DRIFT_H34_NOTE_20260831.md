# H34 — KuGou auto overlay + late attach + visual drift + native-event COM guard

Field closure date: 2026-08-31.

## Confirmed field failures

The Win10 19045/frozen log shows that KuGou track identity and lyrics can be acquired automatically while presentation still depends on a later manual Start click. It also shows that user rail gestures themselves are observed correctly once a rail is learned, so the remaining problem is not the basic WH_MOUSE_LL seek hook.

A second independent failure appears after the next track starts near zero: the shared visual fallback accepted unrelated/incorrect rails at roughly 190 s, 153 s and later ~64 s while the current local track clock was only around 12 s. Large visual/local disagreement was therefore being treated as an invitation to re-anchor instead of a reason to demand stronger proof.

The same log also records Windows exception 0x8001010d while cyclic GC is releasing a comtypes object inside Qt nativeEvent. H34 keeps COM/UIA ownership unchanged but prevents cyclic GC finalizers from running inside the input-synchronous native message callback.

## H34 contract

1. A deliberate QQ/NetEase -> KuGou player switch while LimbusLyric is already running is treated as an existing-playback late attach. The scoped request reuses the reviewed `startup_existing` bind contract; synthetic song-zero is forbidden until a real clock, physical visual proof, or user seek exists.
2. Successful current-track KuGou auto lyrics own presentation immediately. A stale generic suspension flag is cleared before the historical launch chain. If the result is loaded but the overlay/timeline still is not running, H34 repairs presentation once without changing media authority.
3. KuGou visual fallback uses the same H30 cross-Windows detector on Win10 and Win11. A visual correction larger than `max(12 s, 8% duration)`, or an unanchored existing-playback attach, must pass a separate second proof across H30 locks: compatible HostV2 geometry plus three coherent forward observations spanning at least 1.1 s.
4. Rejected large-drift candidates also clear the H30 visual lease state, so a rejected false rail cannot continue extrapolating for the next polls.
5. `ControlPanel.nativeEvent` temporarily disables cyclic GC and re-enables it after native dispatch via `QTimer.singleShot(0, ...)`. This specifically keeps comtypes `Release/__del__` out of the input-synchronous callback; it does not reopen Win10 UIA/MSAA.

## Cross-Windows behavior

The KuGou attach/presentation/large-drift rules are Windows-version independent. Win11 keeps stronger UIA/GSMTC evidence when available; Win10 frozen keeps the H22/H23/H24 fail-closed UIA/MSAA policy. Only the common visual fallback and session lifecycle semantics are hardened.

## Regression lock

`installer/CHECK_KUGOU_AUTO_OVERLAY_LATE_ATTACH_VISUAL_DRIFT_H34_REPLAY.py` replays the field-style false rail sequence and the player-switch/auto-overlay/nativeEvent contracts. Canonical release suite: 94 gates including H34.
