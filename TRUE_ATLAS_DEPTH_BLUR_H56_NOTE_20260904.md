# H56 True Atlas Depth Blur

H54's immutable per-line random Z ownership remains authoritative. H56 changes only the optical renderer.

## Why H55 was retired

H55 drew the same sharp glyph Atlas at several translated offsets. That can make bloom/ghosting, but it is not a spatial low-pass and becomes visibly dirty at large radii.

## H56 renderer

- H54/H55 legacy haze callbacks are hard-disabled after H55 activation.
- A deep lyric line takes glyph pixels from the already-built shared song Atlas.
- Every used glyph is copied into an isolated transparent padded cell, so packed neighbours cannot bleed into it.
- The cell is repeatedly downsampled with `Qt.SmoothTransformation` and reconstructed through the same pyramid. This produces a real low-pass of text, outline, shadow and user Glow pixels.
- Filtered glyphs are repacked into a row-scoped Defocus Atlas. Deep layers may also get a broader Bloom Atlas.
- Logical glyph metrics are **not** expanded when transparent blur padding is added; the audio-emphasis anchor and fragment centre remain identical to the sharp renderer.
- The active row renders Bloom (optional), Defocus, then a depth-dependent sharp core through the existing `QPainter.PixmapFragment` batch geometry.
- A completed row inherits the current filtered-Atlas cache. Held historical rows use the same cached textures. Exit animation immediately returns to the authoritative H51/classic renderer so per-character masks cannot leave a full-row blurred ghost.
- Sparse dirty bounds are enlarged for held blurred rows so expanded filtered pixels are not clipped or left stale.

## Performance / fallback

No Pillow, NumPy, PyOpenGL, QML or `QOpenGLWidget` dependency is added. The translucent top-level QWidget, multi-screen ownership and packaging dependency graph remain unchanged.

Filtered Atlases are built once per row/style/filter-level key and cached, with glyph-count, atlas-size and wall-clock build limits. A failed/over-budget key is cached as a sharp fallback rather than retried every frame.

Renderer pressure level 1 drops Bloom and limits Defocus to two pyramid levels while restoring more sharp core. Pressure level 2+ disables all H56 extra passes and uses the original sharp Atlas.

## Visual contract

At default 55% strength / six layers:
- layer 1 is completely sharp;
- middle layers become progressively low-pass filtered;
- layer 6 uses four Defocus pyramid levels plus a five-level Bloom texture and keeps at most 16% sharp core.

At 100% / layer 6 the sharp core is at most 7%.
