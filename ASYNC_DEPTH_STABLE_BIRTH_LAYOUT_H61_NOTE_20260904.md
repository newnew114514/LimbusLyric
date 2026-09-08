# H61 · Async depth fallback + stable birth-only layout

H60 field logs exposed a concrete presentation failure chain:

1. the full-song styled Atlas legitimately hit the existing 850 ms worker fuse;
2. H60 then built a row-local styled Atlas synchronously from `_shared_song_fragment_atlas()`, which is queried from paint;
3. on `赤と青`, one row-local build took about 101 ms and H57 composition about 29 ms, producing a ~137 ms paint;
4. H11's hard-paint safety renderer then entered `plain-glyph`, which intentionally omits Glow/vector decoration and simplifies history.  Because `paint-hard-budget` had no bounded recovery, one transient spike could keep the rest of the session visually degraded.

H61 retains the 850 ms full-song fuse. Row-local source Atlas rasterization is now performed on a below-normal/background Python worker using the existing QImage-safe atlas builder. The worker returns through the existing Qt queued signal; only QPixmap conversion/cache installation happens on the GUI thread. The paint-time shared-Atlas callback never rasterizes a row.

A row may accept a newly completed fallback Atlas only during the first 320 ms / early glyph phase, then the selected source material is frozen for that row. Late completion cannot swap an established visible row. A `paint-hard-budget` emergency is also time-bounded and automatically returns to the normal renderer; a genuinely repeated overload can re-arm it.

The center feature is redesigned after reviewing mature label-placement approaches used by map rendering. The useful common properties are deterministic/stable placement, rectangle collision testing, bounded candidate regions, and no continuous movement of labels after placement. H61 therefore bypasses H59/H60 post-push for new rows. It generates a deterministic Bridson-style blue-noise candidate set over the viewport, treats already-visible subtitles as read-only collision obstacles, rejects candidates that are vertically off-screen or intersect the protected center corridor when center admission is not allowed, then commits exactly one newborn anchor. Existing subtitles are never moved.

The existing 0–100% control remains an admission quota: 0% never admits center, 100% does not restrict center, intermediate values use a deterministic accumulator to avoid visible random clusters.
