# Runtime Fix R2 — 2026-09-08

R2 is based on FRONTEND_RUNTIME_RESTORE_R1. It intentionally preserves the R1 frontend/runtime installation chains and does not consolidate lyric paint, exit-effect, record-animation, or ControlPanel wrappers.

## Runtime fixes

- QQ UIA mm:ss duration can become player-owned duration only after advancing-time proof while playing; lyric-provider duration is no longer required to unlock the player clock.
- QQ lyric-search HTTP 5xx failures use a bounded circuit breaker so repeated provider failures do not serially delay every search attempt.
- Cross-provider precise lyrics found before player duration is known stay provisional instead of becoming final quality-3 timing authority.
- KuGou keeps a monotonic holdover from a trusted HostV2/UIA anchor while background UI evidence is unavailable.
- A grossly inconsistent KuGou visual rail is quarantined for the current transport generation instead of repeatedly re-proving the same stale rail. A real user rail gesture clears that quarantine.
- KuGou same-track transport-generation changes reset visual/history/fading epoch state while keeping lyric data, visual resources, caches, and user effect settings.

## Safety boundary

R2 does not change the R1 frontend runtime installation order. `CHECK_FRONTEND_RUNTIME_PARITY_R2.py` locks the major wrapper chains against the R1 baseline.
