# H95F10F17 Exit Material Continuity + Multi-row Budget

## Field evidence
The F15 field log showed the discontinuity at the exact history/fading transition:

- `H37紧急历史弹幕动态保留 | history/fading=shake+glyph-scale | glow/vector=skip`
- immediately followed by `H95F10F9冷缓存帧保护 ... renderer=existing-plain-glyph` even when only one translated glyph was missing.
- with `visual_count=4 | history=2 | fading=1`, paint rose to roughly `avg=17.55ms / p95=22.06ms / max=47.80ms` despite ~99.9% sprite hits.
- old western history rendering used `fill alpha = alpha-100` while outline/glow kept the row alpha, making outline color dominate late in exit.

## F17 ownership change
F17 changes material admission only; mature entrance/exit progress formulas remain H59/H62-H76 owned.

1. Cold fallback is lane/glyph-local. A translation-only miss may suppress/redraw only the translation lane. It cannot downgrade primary/history.
2. Ready primary/history glyphs reuse existing styled sprite/fragment/depth/blur materials. Only the actually missing active glyph may use the existing plain emergency primitive.
3. History/fading rows prefer already-published optical material and use one row alpha for baked text/stroke/glow. The historical western face-alpha-minus-100 split is retired for history material only.
4. Translation history material is suppressed only when its own material is not ready; primary row material remains intact.
5. GUI QImage->QPixmap installs are time-budgeted (`<=1.35ms`, max 5 ready glyphs per tick) rather than fixed one-glyph draining.
6. Current-row H61 fallback scheduling yields briefly while visible glyph/install backlog exists. Future-row H61/H69 admission remains owned by F14.
7. A compact style diagnostic reports resolved text/stroke/glow/exit state so apparent color changes can be attributed to the actual preset/material rather than guessed from screenshots.

## Protected boundaries
No provider/search/clock/seek identity logic is changed. No `FadingLine.draw` replacement is added. No QPainterPath/text raster build is introduced in paint. Existing H51 typography, H57 depth, H62-H69 blur, H70/H71 exit profiles/flavor, and F14 scheduler remain owners of their semantics.
