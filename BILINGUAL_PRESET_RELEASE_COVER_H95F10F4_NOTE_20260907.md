# H95F10F4 — Bilingual preset parity + release-aware cover identity

## Field regressions closed

- Keeps H95F10F3's cached-sprite bilingual performance closure, but removes its simplified secondary-lane presentation shortcut.
- The translation lane now resolves typography from the translation text itself (H51 script-family and per-line size-range rules) instead of scaling an already-resolved primary-language font.
- Translation entrance uses the mature user-selected entrance resolver/attack/easing/motion, and translation shake uses the mature living-shake engine with the user's intensity/speed.
- Translation history keeps its own glyph order while reusing mature whole-row exit transforms and user-selected per-character/wipe/blur semantics; no mapping to primary glyph indices and no paint-time QPainterPath rebuild is reintroduced.
- Bounded sprite prewarm now primes the translation's own resolved script font and remains pressure-aware/GUI-idle.

## Cover identity closure

- H95F2 title/artist/duration matching was track-strict but not release-strict: multiple albums/singles containing the same recording could still be treated as one valid cover identity.
- A cover-only GSMTC metadata probe reads album/release evidence on its own worker and revalidates session title/artist; protected playback polling is untouched.
- Artwork selection includes release/album identity when available and uses a release-scoped cache key/schema.
- If release evidence is unavailable and multiple strong release candidates remain, artwork is rejected rather than choosing the first candidate.
- A separate H95F10F4 migration clears artwork-derived colour evidence accepted under the earlier track-only selector while preserving the existing H95F2 migration contract.

## Protected authority

- No player clock, seek, lyric provider/search, precision-upgrade, primary precise/classic renderer, or packaging dependency ownership is changed.
- Cached-sprite rendering remains the bilingual hot path; the H95F10F2 vector regression stays retired.
