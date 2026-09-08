# H37P1 Release Gate Portability

H37 runtime behavior is unchanged. This packaging patch removes a scheduler/timer dependency from `CHECK_KUGOU_WIN10_CRASH_HARDENING_H22_REPLAY.py`.

The historical replay simulated a slow provider using `time.sleep(0.012)` and then compared the measured call time against a 5 ms threshold. On some Windows/VM build environments this synthetic timing test can fail spuriously, reporting `calls=2`, even though the production H22/H33F1 one-shot mandatory skip is present.

H37P1 tests the same slow-fuse branch deterministically by setting the replay-only threshold to zero. The production constants and runtime H22/H33F1 implementation are not changed.
