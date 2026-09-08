# H54 Random Fixed Depth + Multiscript Font Preview

## Why H54 exists

H53 fixed literal center-frequency avoidance and added an opt-in depth presentation, but its depth model was age-based: each new lyric pushed every older row one layer farther away. In real use this looked like the whole subtitle stack shrinking on every line change rather than independent objects living at different depths.

The font hover popup also still used the old `歌词预览` filler text and did not make Japanese/Korean coverage obvious.

## H54 depth ownership

When depth is enabled, each lyric row samples one integer depth layer from `1..N` exactly once before its placement is measured. The active row keeps that layer while it is current, and `_make_history_line` copies the same layer into its held/fading snapshot. Existing rows are never renumbered because a newer lyric appeared.

A newly appearing lyric may therefore be born directly in the farthest layer.

Depth uses three bounded presentation cues:

1. modest draw-matrix recession (layer 1 remains 100%; farther layers become smaller according to strength without changing font/Atlas signatures),
2. atlas-only subpixel haze copies around distant glyphs,
3. slightly softer main atlas opacity at distance.

The fixed recession is applied at draw time, so it preserves the current font/style signature and shared song Atlas. The haze reuses that existing immutable glyph atlas. It does not create a QImage blur, QGraphicsBlurEffect, Gaussian blur, new glyph rasterization, provider call, or lyric-clock work per frame. Under renderer pressure level 1 the haze pass count is reduced; at pressure level 2+ it is disabled and the normal text renderer remains authoritative.

If a row already has user glow baked into its atlas, the offset copies spread that glow farther and softer. If glow is disabled, the distant glyph itself gets a subtle low-alpha halo, giving a defocus cue without changing the saved glow preference.

H53's age-based matrix depth flag is explicitly disabled by H54; H53's center avoidance remains active.

## Font hover preview

The hover popup now shows:

- Chinese + Latin/numerals,
- Japanese kanji/hiragana/katakana,
- Korean Hangul.

Japanese and Korean rows also show a direct `✓` / `△ 缺字` capability hint using the existing H51 `inFontUcs4` coverage check. The old `歌词预览` filler is removed.

## Compatibility

- Feature remains opt-in through the existing depth checkbox.
- Existing H53 depth config keys are reused, so users do not lose their saved enabled/strength/layer values.
- Center-frequency behavior is still owned by H53.
- No MediaSessionSync, auto-lyric transaction, player clock, seek, native accessibility or packaging runtime path is modified.
