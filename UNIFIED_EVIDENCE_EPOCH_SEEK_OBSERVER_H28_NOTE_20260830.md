# H28 — Unified Evidence Epoch + Seek Observer Closure

Field evidence basis: Win10 19045 frozen KuGou/NetEase log from 2026-08-30 and the earlier Win11 KuGou log.

## Confirmed defects closed

- KuGou transport epoch changed tracks correctly, but LyricWindow could retain the previous track position/precision handoff. The field log showed a new-track local rail near 202ms while precise handoff used 9152ms. H28 resets renderer position, precision lease, visible history and stale seek state at the same KuGou track epoch, then refreshes the current MediaSync position immediately before an early precision upgrade.
- KuGou auto-cache keys with duration key 0 are version-unsafe. H28 removes unknown-duration KuGou cache rows at load and before an unknown-duration auto search; duration-keyed rows remain eligible.
- Win10 frozen KuGou can lose cached host geometry while UIA/MSAA are intentionally disabled. H28 publishes the official `kugou_ui` host rectangle using EnumWindows + DWM only and seeds a geometry-only progress-rail observation band. WH_MOUSE_LL remains the input witness; H28 does not inject mouse input.
- A committed KuGou rail event now records an H28 seek observation transaction bound to the current track epoch. Existing local reanchor semantics are retained, but geometry can be available on the first normal rail click instead of requiring a prior training drag.
- NetEase liveness now has a PSAPI positive-only fast path. A positive executable match skips the historical Toolhelp/tasklist chain; absence is UNKNOWN and cannot create death authority.
- When H26 NetEase static-rail proof remains pending for a dwell period, H28 may invoke the historical H25 temporal motion detector as a second independent screen-pixel proof. Accessibility remains closed and a static/unproven line still has no time authority.

## Compatibility boundary

H1-H27 historical method bodies remain source-locked. H28 is installed as the final outer layer and exposes explicit `_limbus_layer = 'H28'` ownership markers so release replay checks the callable that actually owns runtime behavior. Win11 KuGou continues to use its accumulated HostV2/UIA path; the new pure-Win32 KuGou geometry rescue is restricted to the Win10 frozen safe profile.
