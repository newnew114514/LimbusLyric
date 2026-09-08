# H33F1 — H22 Fuse Next-Call Hardening

Field packaging on Windows collected one failure from the unchanged H22 replay: `slow-provider fuse did not suppress second call: calls=2`. The H22 replay passes in isolation, but the canonical runner executes gates concurrently. The historical guard used only a monotonic deadline; an extreme scheduler/VM pause beyond the shortened replay fuse could let the logically immediate second call re-enter the provider.

H33F1 adds a one-shot mandatory next-call barrier whenever slow/no-range HostV2 UIA arms a fuse. The barrier is consumed by the next invocation even if wall-clock advanced past the fuse deadline. A changed HWND clears it so a genuinely new KuGou provider instance still receives a fresh capability attempt.

The historical H22 gate is unchanged. `CHECK_H22_FUSE_NEXT_CALL_H33F1_REPLAY.py` additionally simulates a 45-second scheduler jump after a 30-second fuse and verifies that the next logical call remains suppressed.
