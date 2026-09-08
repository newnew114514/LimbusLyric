# Liveness Corroboration H18 — 2026-08-28

H18 is a narrow false-dead closure on top of H17. It does not change lyric provider selection, player position/seek authority, QQ/KuGou/NetEase clock arbitration, DIY ownership, or presentation timing.

## Evidence from H10F4 field logs

Two independent real-user patterns were observed:

1. Process enumeration can hang for many seconds. H11/H17 already bounds this path.
2. More importantly, Toolhelp can also produce a fast `False` during startup/switch even though the same player becomes positively detected a few seconds later. H10F4 could accumulate three such samples immediately and retire an actually running player.

The log message `系统媒体会话归属隔离 | selected=<player> | rejected_current=<other>` is **not** positive GSMTC evidence for `<player>`; it means no strict matching session was available and the unrelated global-current session was correctly rejected.

## H18 changes

- A fast Toolhelp `False` is no longer death evidence by itself. It must be corroborated by H11's independent, deadline-bounded `tasklist` probe.
- If tasklist is unavailable/times out, the combined observation is `UNKNOWN`, never `DEAD`.
- A new player liveness epoch has a 9.0s negative-only grace period. Positive `True` still applies immediately.
- After grace, corroborated negative evidence must persist for 1.8s before it is allowed into the existing multi-confirmation dead-streak state machine.
- A strict process-affine GSMTC session is recorded only while the already-public transport state is `playing` or `paused`; H18 does not add a second GSMTC playback-info call. This short-lived witness may veto a negative and may rescue `UNKNOWN -> ALIVE`; it never rewrites an explicit confirmed `False` by itself.
- Existing player-dead retirement remains unchanged once the corroborated/dwelled liveness state reaches confirmed `False`.

Dedicated replay: `installer/CHECK_LIVENESS_CORROBORATION_H18_REPLAY.py`.
