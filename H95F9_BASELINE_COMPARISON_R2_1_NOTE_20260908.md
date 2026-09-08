# H95F9 baseline comparison for R2.1

Compared source:
- H95F9 audited fixed (2026-09-07): 75,949 lines.
- Runtime Fix R2 (2026-09-08): 81,907 lines before R2.1 convergence edits.

Direct runtime-install counts in H95F9 vs R2:
- `LyricWindow.paintEvent`: 7 -> 10
- `LyricWindow._make_history_line`: 15 -> 18
- `LyricSearchEngine.search`: 3 -> 5
- `ControlPanel.__init__`: 52 -> 54
- `FadingLine.draw`: 17 -> 17
- `MediaSessionSync.bind_track`: 6 -> 6
- `MediaSessionSync.snapshot`: 4 -> 4

Important interpretation:
- H95F9 is not a separate/simple playback architecture. Most transport/liveness/exit machinery already exists there.
- R2 adds useful safety/capability layers, but later bilingual/precise retrieval and material-prewarm layers can increase latency/work.
- The H95F9 fast auto-search path did not require an H95F10 same-provider bilingual pair before first display. R2.1 restores that first-screen behavior while retaining later bilingual/precise upgrade.
- `FadingLine.draw` itself is not reverted: current visual effects remain installed. R2.1 does not claim that the remaining multi-row render cost is solved without new field measurements.

R2.1 policy: use H95F9 as a behavioral/performance reference, not as a wholesale rollback target.
