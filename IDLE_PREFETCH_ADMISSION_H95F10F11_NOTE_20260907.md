# H95F10F11 — Idle Prefetch Admission

F11 extends the F9 shared glyph prewarm runtime without adding another active raster lane.

- Visible missing glyphs never wait for admission.
- Current-row full prewarm briefly yields to mature H61/song-atlas/translation-depth work, then proceeds after a bounded wait.
- Speculative neighbour work is disposable under contention rather than competing for CPU.
- Idle lookahead expands from N+1 to N+1/N+2; N+2 is delayed and lower priority.
- Stale line/track generations cancel work through the existing F9 token authority.
- The original F9 daemon is left blocked on its old empty queue; F11 swaps in a new queue and one active worker rather than attempting unsafe thread termination.
- No provider, clock, seek, H61/H69, depth, typography, or effect semantics are changed.
