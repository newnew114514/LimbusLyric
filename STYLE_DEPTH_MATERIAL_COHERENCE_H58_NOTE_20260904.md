# H58 Style / Depth Material Coherence

Field evidence from H57 showed a style-coherency failure rather than a depth-optics failure.
The base Song Atlas already rasterizes text, shadow, outline and glow before H56/H57 low-pass
composition. However the legacy live edge/glow controls mutated the current and historical row
style fields immediately without rebuilding the matching Song Atlas. That changed the fragment
style signature, forced sprite/vector fallback, produced sharp outline/glow over a depth row and
could trigger the expensive emergency plain-glyph renderer.

H58 treats decorative style as immutable row-birth material:

- text + shadow + outline + glow are rasterized together before H57 depth composition;
- live edge/glow edits are coalesced for 180 ms and prewarm a matching Song Atlas;
- existing current/history/fading rows retain the material they were born with;
- a pending material commits only at a lyric boundary and only after the exact Atlas key exists;
- a prewarm that re-hits the performance fuse keeps the previous valid material rather than
  committing to a sharp vector fallback;
- fixed font and fixed color changes join the same queued visual-style path when random style is off;
- no MediaSessionSync/provider/timing authority is changed.

This also removes the field-log performance cliff where a style mismatch materialized thousands
of vector path elements and caused a 140 ms paint-hard-budget emergency downgrade.
