# H95F8 · Lyric Payload Firewall + Long-Line Containment + Adaptive High-Refresh

H95F8 is a safety/performance closure over H95F7. It does not replace lyric timing, seek, player identity, or the existing renderer.

- Provider payloads must produce parseable lyric events before they can enter the automatic lyric cache or display path. Instrumental boilerplate remains exempt.
- The historical `non-empty payload + parse_lrc()==[]` incident is denied before cache admission and again before display.
- Provider-specific search functions are guarded before `LyricSearchEngine.search` evaluates cross-provider quality, so an invalid primary payload becomes an absent candidate and the existing safe fallback ladder can continue.
- Very large visible lines are rejected when they are machine-shaped (URL/API/JSON/metadata) or exceed the hard provider-line visual budget. Manual untimed text keeps the legacy renderer fallback because it never passes through the provider firewall.
- Existing auto-cache rows are revalidated on load and unsafe rows are removed and persisted.
- 100Hz displays use a 10ms low-pressure cadence; 116Hz+ uses an 8ms low-pressure cadence (about 120fps). Paint pressure falls back through 10/12/16ms. 60Hz keeps the existing display-aware cadence.
- Active reveal/shake timers are retimed at most every 500ms. Lyric timestamps and player clocks are unchanged.

Primary regression case: the old `战斗基 / LICK WHITE` style failure where a provider returned non-empty control text but zero parsed rows must result in no auto-cache admission and no visual lyric payload.
