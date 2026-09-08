# H60 · Depth fuse fallback + center stability + preview UI cleanup

Field H59 evidence showed three presentation defects without a new player/clock root:

1. A full-song styled Atlas hit the existing 850ms performance fuse. That fuse is retained, but H57 depth then had no shared pixel source and fell back to sharp sprite/vector rendering.
2. H59's center-corridor post-push could recompute perspective into a *worse* overlap and still commit it repeatedly.
3. Script-specific QFontComboBox controls already had rich hover previews; an ordinary tooltip repeated the same explanation over the popup and obstructed the sample text.

H60 keeps the song-level fuse unchanged. Once it fires, only a deep active lyric row may build a row-local styled Atlas from that row's unique glyphs. The row-local Atlas is frozen for the visible row and inherited by history/exit, then enters the existing H56 low-pass + H57 composite pipeline. No provider, lyric transaction, timing, or seek authority is changed.

H60 replaces H59's center push helper with a transactional evaluator. Every candidate starts from the original anchor, recomputes perspective, and is committed only if corridor overlap strictly decreases. Several stronger side/corner candidates are evaluated for projective layouts; if none improves the overlap, the original placement is retained rather than being made worse.

The settings UI now removes ordinary tooltips only from font controls that already have rich hover previews (and their redundant inline/DIY preview hints). Actionable tooltips on unrelated controls remain.
