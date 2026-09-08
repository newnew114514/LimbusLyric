# POST-RELEASE RESPONSIVENESS H11 — 2026-08-25

## Scope
H11 is a targeted post-release closure on top of RC11/V29/H10F4. It was driven by the important raw-log bundle collected from real users after release. The goal is to remove unbounded GUI/control/fetch/liveness failure modes and correct several presentation/identity state bugs without redesigning the three provider-specific time authorities.

## Reconfirmed raw-log symptoms
- QQ: `qq_gesture` reached roughly 60 s and one player-read sample roughly 120 s.
- NetEase: `netease_click` reached roughly 3.16 s in the same player-read round; independent liveness observations degraded into multi-second/tens-of-seconds ranges.
- KuGou: manual precise/KRC fetch showed a ~38 s successful case and other sessions with >47 s / near-two-minute lack of terminal result; ordinary LRC provided a fast control case.
- KuGou: failed new-track/translation transactions could leave old presentation state reachable; Host window titles can be malformed/noncanonical.

These timings are evidence from the archived user logs. H11 does not claim the old reports correctly identified every root cause; source review narrowed those roots before changes were made.

## Changes
### GUI control isolation
QQ pointer-gesture and NetEase page/hover interaction calls exposed from `MediaSessionSync.snapshot()` are runtime-wrapped as fire-and-forget control requests. Each channel owns one daemon worker and an Event-coalesced queue. An already-stuck channel does not spawn replacement workers. Watchdog telemetry is emitted independently of call return.

### Manual lyric fetch isolation
Manual fetch is a generation-scoped asynchronous transaction. Identity probing and provider search run outside Qt. In precise mode, an ordinary lyric may be applied first and precision upgraded later. Stale generations are dropped. A bounded GUI transaction deadline prevents permanent “reading” state; precise background work can finish or be ignored without blocking UI.

### Player liveness isolation
H10's three-sample death proof remains the policy. H11 changes the observation mechanism: a Toolhelp helper that exceeds its native budget is quarantined; liveness continues through a separately bounded `tasklist` subprocess. Timed-out Toolhelp results cannot later publish stale alive/dead. `tasklist` timeout, nonzero exit, exception, or blank output is UNKNOWN rather than dead. Only a successful process listing can contribute a false/dead observation.

### QQ unknown-status cold start
A new outer fallback can prove active playback while QQ reports `status=unknown`, but only from high-confidence `qq-time-pair-validated` samples that advance repeatedly at a plausible wall-clock pace with consistent source identity. Candidate/static/hover-like data cannot arm the fallback. Explicit playing continues through the existing baseline.

### Presentation ownership and translation preference
Once a new track is confirmed, it owns the presentation even if lyric search fails; a prior payload may remain cached but cannot revive merely because the new fetch failed. A later successful current-track payload releases the block. `trans_only` remains a persistent user preference when one song lacks translation rather than rolling the preference back.

### KuGou identity/discovery
Malformed HostV2 titles are sanity-checked before being allowed to shortcut more credible metadata. Repeated Host misses use negative-cache/backoff while explicit force events can request immediate discovery. Host/visual evidence is still not allowed to fabricate a playback position when no real position exists.

### Rendering pressure fallback
If the whole-song atlas is still inflight/performance-fused or a real paint exceeds the emergency threshold, the presentation can use a cheaper glyph route and reduced visual cadence. Timing/seek authority is untouched; this is a presentation survival mode for pathological font/render load.

### Bounded exit
Exit invalidates current transactions, stops timers, hides UI, asks providers/media sync to stop outside the GUI wait path, quits Qt, and arms a last-resort hard-exit watchdog. This is a safety closure for the observed “tray exit but process remains” symptom; it does not assert a single proven historical root cause.

## Regression coverage
`installer/CHECK_POST_RELEASE_RESPONSIVENESS_H11_REPLAY.py` executes injected slow/stale cases for GUI-control isolation, liveness quarantine/stale-drop/tasklist result semantics, QQ unknown advancement, manual fast-before-precision behavior, presentation ownership, trans_only persistence, KuGou title/backoff, render fallback, and exit structure.

The canonical TSV also includes V14/V16/V17 replays that existed in the tree but were previously omitted, bringing the canonical count to 69. Existing RC11/legacy/KuGou/QQ/H10/H10F2/H10F3/H10F4 contracts remain separate gates.

## Intentionally not changed
- QQ Software-2 formal time/seek authority is not replaced by geometry or a one-sample Text value.
- KuGou Host/Range/rail authority is not generalized into a fake GSMTC clock when position is unavailable.
- NetEase native adapter remains the default path.
- Existing caches are not blindly deleted on a failed new-track fetch; display ownership, not cache destruction, is the correctness boundary.
- No broad provider abstraction/refactor was performed.

## Validation boundary
Linux-side source/replay/fault-injection tests can verify these contracts and prevent many deterministic regressions. They cannot substitute for a real Windows machine running the exact QQ/NetEase/KuGou builds, security software, UIA tree, GPU/font stack, and installer. Future real-machine logs remain required to call environment-specific behavior fully verified.
