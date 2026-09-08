# H91 — Draggable Workspace / Media-First Hero / Shared Cover

H91 is a presentation-only closure based on H90 field feedback.

- The blank area of the top page-navigation strip is a vertical workspace splitter. Drag up to compress the Hero / record area and give space to settings; drag down to restore. Navigation buttons keep normal click ownership. The selected Hero height persists.
- The front Hero follows process-affine media title/artist immediately instead of waiting for the lyric transaction to replace `_loaded_song`. This changes presentation only; lyric, clock and seek ownership are unchanged.
- Record artwork and “follow cover colour” now share the same disk artwork acquisition pipeline. A successful artwork fetch populates both the record and the colour cache. A colour-only legacy cache cannot recreate an image, so one artwork fetch is still required before the record can display it.
- QQ artwork matching now understands bracket-heavy title forms and uses title/artist/duration evidence. NetEase remains a fallback.
- Old artwork retires after a bounded grace period if the new track has no art.
