# RC all-player zero-touch / startup late-attach audit

Scope: startup lifecycle only. This patch does not relax QQ seek/hover/GSMTC authority, NetEase native-log authority, or KuGou Host V2 / 21 golden methods.

## Problem reproduced

- NetEase already auto-armed at application startup and can attach to an existing mid-song native-log position.
- QQ / KuGou previously only warmed their adapters. If the player was already playing before LimbusLyric started, the first track could have lyrics but no trustworthy current-position anchor.
- Existing QQ background-new-track display continuation solves a *later track change*, not an already-mid-song first attach.

## Reviewed behavior

- Selected QQ / NetEase / KuGou now all enter the same zero-touch automatic track lifecycle when auto tracking is enabled.
- First attach is explicitly marked `startup_existing`; detection latency is never treated as song position zero.
- QQ startup-only hidden UIA current/total pair requires expected-duration match and three coherent samples before publication.
- KuGou startup-only hidden RangeValue requires native Range duration match and the existing three-sample causal proof before it can seed the existing rail-local master.
- If no real position witness is available, the code waits. It does not fabricate a playback position.
- Switching the explicit built-in player selection re-arms zero-touch automatically; pressing Start is not required.
- Strict selected-player affinity remains. The patch does not automatically switch to whichever system media session happens to be current when multiple players are open.

Gate: `installer/CHECK_ALL_PLAYER_ZERO_TOUCH_LATE_ATTACH_REPLAY.py`.
