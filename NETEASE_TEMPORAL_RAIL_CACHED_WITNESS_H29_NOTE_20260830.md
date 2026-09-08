# H29 NetEase Temporal Rail + Cached Process Witness Closure — 2026-08-30

Field evidence from Win10 19045 / frozen Python 3.12.6 showed H28 did not close the NetEase clock:

- H28 PSAPI positive liveness skipped `tasklist`, but still enumerated the full process table and degraded from ~0.9s to ~5.8s per probe.
- H26/H27 static visual candidates stayed `proof-pending` (typically 4 proofs) for the full session.
- H28's advertised temporal fallback re-entered H25's old motion+infer path and never acquired authority.
- Native elog detector remained unavailable/timed out, so the screen-only Win10 safe lane must stand on its own without UIA/MSAA/Chromium traversal.

H29 closes those exact gaps:

1. Win10 safe NetEase no longer routes through H26/H28 for its primary visual clock. H29 samples the lower transport strip directly.
2. Time boundary comes from compact multi-row *temporal pixel motion*. Static colour candidates supply geometry only and can never be the clock boundary.
3. Around the temporally moving point, the local two-tone rail extender owns x0/x1. Broad static-row geometry is fallback-only.
4. Three coherent samples spanning >=720ms are required before authority; static distractors and unrelated animation cannot lock.
5. A verified anchor may extrapolate for at most 2.6s across an occasional missed frame; after that absent evidence returns UNKNOWN.
6. NetEase window discovery caches validated HWND + PID + rect. Positive liveness then checks only that cached PID with `GetExitCodeProcess`; no `EnumProcesses` and no tasklist on the positive path.
7. Win11/non-safe visual behavior delegates H28 unchanged.

Dedicated replay:
`installer/CHECK_NETEASE_TEMPORAL_RAIL_CACHED_WITNESS_H29_REPLAY.py`

Canonical release suite: 87 gates including H29.
