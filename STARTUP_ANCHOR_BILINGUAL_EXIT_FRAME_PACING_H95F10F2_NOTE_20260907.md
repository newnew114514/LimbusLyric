# H95F10F2 — Startup anchor, bilingual exit ownership, frame pacing

## Field evidence

The H95F10F1 field log exposed three separate presentation defects:

1. A cold-start QQ rail escape path could commit a single transient validated Text sample. In the captured session a rail hint around 125 s accepted a ~123 s Text value, while subsequent Text samples immediately returned to 5/6/7 s. The overlay therefore jumped far from the real playback stream before the ordinary seek FSM recovered.
2. The bilingual translation lane was drawn after the mature primary `FadingLine.draw()` chain. Its per-character/wipe state was recomputed from translation character count, so it did not share the primary H70/H71/H76 exit order, random seeds or motion.
3. The secondary lane could schedule a second full-song atlas and synchronously rasterize fallback glyph sprites from `paintEvent`. Field performance showed an 799–856 ms song-atlas build, GUI stalls up to ~188 ms, and large frame spikes during song/precision transitions.

## Closure

- QQ cold-start rail prelock now requires three coherent duration-matched, post-release validated Text samples spanning at least 260 ms. A large backwards discontinuity restarts the cluster. The existing rail/seek authority is delegated only after this proof; normal post-lock seek ownership is unchanged.
- Translation fragment exits map each translated glyph onto its corresponding primary glyph index and reuse the primary per-character scatter/seed/motion or primary geometric wipe state. Whole-row effects reuse the primary group-motion envelope. `blur_decay` shares timing/visibility/spatial expansion but remains a separate glyph material because the primary blur texture is baked before the secondary lane exists.
- Translation no longer schedules its own full-song atlas. Existing cache hits may still be reused, but new secondary atlases are not built.
- Translation paint no longer calls `_hires_glyph_sprite`; visible translated glyphs use bounded vector batches with a process-wide immutable path cache. Primary atlas/fragment rendering is unchanged.
- Bilingual dirty regions reserve extra exit-motion padding so the larger primary-state-mapped translation motion cannot leave stale pixels.

## Regression coverage

`installer/CHECK_STARTUP_ANCHOR_BILINGUAL_EXIT_FRAME_PACING_H95F10F2_REPLAY.py` verifies:

- the captured transient 123 s → 5/6 s startup pattern cannot invoke the legacy one-sample commit;
- a genuine coherent three-sample rail seek still delegates exactly once;
- translation exits use primary glyph state and do not use the old translation-owned exit helper;
- no translated full-song atlas scheduling and no paint-time sprite rasterization remain;
- H95F10F2 does not replace general player position/seek/parser authority.
