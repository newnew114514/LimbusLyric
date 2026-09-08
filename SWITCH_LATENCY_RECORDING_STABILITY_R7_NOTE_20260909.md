# Switch Latency + Recording Stability R7

Release-only scheduling closure for v1.8.9.134.

- QQ auto ordinary first-screen search no longer waits for two foreign providers in series. The fast stage races at most two mature ordinary-provider paths and returns the first usable payload; the existing duration/version validator still decides whether it may be displayed.
- Precise lyric search, provider parsers, player clock/seek ownership, and cross-provider precision verification are unchanged.
- New lyric sessions defer whole-song Atlas construction for about 920 ms and speculative neighbour/future work for about 240 ms. Current/visible rows keep the existing sprite/vector fallback and all effect formulas.
- R6 late-frame quiet remains active as a reactive safety net.
- Feedback uses the local in-app copy panel; mailto is optional only.
