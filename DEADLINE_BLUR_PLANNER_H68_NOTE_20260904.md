# H68 Deadline Blur Planner — 2026-09-04

## Field evidence
The H67 field session exposed two distinct timing failures. In mixed/slow TIAN TIAN sections the controller decelerated near its fixed 0.875 pre-eviction target and then had to accelerate again when the next capacity release arrived, producing a visible late gear change. In the ultra-dense 熱異常 section, line gaps repeatedly fell to 117–150 ms while H67 clamped cadence to at least 420 ms and capped its speed multiplier; fading rows accumulated from 3 to 10. The log does not show a pressure/burst direct-drop in that exact interval—the backlog itself made several exits appear to collapse together.

## Root cause
H67 optimized for a fixed blur progress *before* capacity eviction. That target is not physically achievable for every song. With H62 hold durations measured in seconds, a 117 ms row cannot reach 0.875 before eviction without a very large velocity discontinuity. EMA cadence also learns a burst after it starts, so a slow-to-fast transition is necessarily late.

## H68 behavior
H68 uses the already-known lyric timeline as a short look-ahead scheduler. For each history row it computes the exact time until normal capacity eviction, adds a cadence-scaled visible release tail, and distributes the remaining blur distance across that whole budget. The row is therefore allowed to enter fading at an intermediate blur level and finish naturally after eviction. Active progress keeps one velocity state; target/deadline changes affect only future velocity. At the handoff to fading, a monotone cubic Hermite segment inherits the current progress velocity and ends at zero velocity, avoiding a restarted ease or late acceleration.

The visible tail is bounded to 320–1250 ms. Dense sections use the short end so the queue remains bounded but still has multiple rendered frames; slower sections get a longer tail. Render pressure is sampled when release begins and may shorten the tail only modestly—later pressure changes cannot retarget an already-running blur exit.

## Direct-disappearance policy
H66 already excludes blur-decay rows from the ordinary render-pressure drop valve. H68 additionally excludes live blur-decay rows from V28 high-density burst direct-clear, even if the user changes the exit selector while an older blur row is still finishing. Instead, blur rows progressively reserve less collision weight as readability falls. Explicit seek, track replacement, stop/reload and user-selected `instant` exit remain discontinuities by design; retaining old-song blur after those operations would be incorrect.

## Scope
No player clock, seek authority, provider identity, lyric search/upgrade, Atlas build, paint-time filter, packaging command or non-blur exit behavior is intentionally changed. H68 is a presentation scheduler layered after H67/H66.

## Regression gate
`installer/CHECK_DEADLINE_BLUR_PLANNER_H68_REPLAY.py` locks exact future-horizon planning, dense-section tail bounds, constant on-plan velocity, velocity-continuous release, burst direct-drop protection, readability-weighted collision reservation, and presentation-only scope.
