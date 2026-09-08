# Release Review Closure H10F2 — 2026-08-20

This is a narrow post-H10F1 release review. It intentionally does **not** change formal QQ Seek/UIA authority, H9 different-song provisional transport, KuGou rail-local/transport authority, NetEase provider authority, or renderer cadence.

## Fixed because real log evidence existed

1. **QQ startup-attach stale display seed**
   - A real H10F1 log showed QQ's validated Text surface transiently reporting 26s -> 21s -> 9s -> 1s during startup/window rebuild.
   - H10F1 allowed the first duration-matched validated sample to seed the display-only startup lane, producing a visible ~28.6s -> 2.4s correction.
   - H10F2 disables the one-sample fast seed only for `startup-attach`. Startup attach now requires the existing advancing-stream proof before retiring the display seed wait.
   - Actual A->B `auto-track` still keeps the H9/H10F1 fast one-sample **display-only** seed; formal clock/Seek authority is unchanged.

2. **KuGou inactive global-hook queue churn**
   - A real H10F1 log showed repeated `酷狗非活动鼠标事件已清理` while QQ was selected/after QQ exit.
   - The WH_MOUSE_LL hook remains installed for reliable KuGou re-entry, but its callback now enqueues events only while KuGou capture is active.
   - Provider switch/death disables capture; KuGou process reappearance re-enables it.
   - `snapshot()` no longer replaces/drains a `SimpleQueue` on every non-KuGou frame; the old cleanup remains only as a defensive one-shot guard.

## Reviewed and deliberately left unchanged

- QQ's ~1.8s duration/version verification window: conservative but not a proven bug; changing it risks wrong-version lyrics.
- QQ formal initial-anchor/Seek FSM: the stale startup issue was confined to the display-only fast seed, so authority thresholds remain untouched.
- KuGou hook installation/uninstallation lifecycle: dynamically unhooking/reinstalling would add gesture-loss/race risk; H10F2 only gates callback capture.
- H8 fault-injection/runtime isolation, Atlas fuse, NetEase/QQ async process-target verification: no regression evidence.
