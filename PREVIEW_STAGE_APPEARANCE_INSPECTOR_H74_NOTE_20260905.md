# H74 Preview Stage + Appearance Inspector

H74 is a presentation-only continuation of H73. It does not change player detection, MediaSync, lyric/provider authority, seek semantics, desktop overlay timing, H70 exit-profile persistence, or H72 dirty/lifecycle ownership.

## User-facing changes

- **Appearance** gains a persistent `LIVE STYLE` preview stage. It reflects the current global font, point size, italic, continuous H12 weight, letter spacing, text color strategy, shadow, outline, glow, and overall lyric opacity. The sample text is editable and remains session-only.
- H12 **font weight**, **overall lyric opacity**, and **cover-follow color** are surfaced in a new Appearance `基础表现` inspector. The old H12 widgets remain the actual config owners and are hidden in Settings; no config keys or migration semantics are changed.
- Appearance cards are ordered as `基础表现 → 样式预设 → 字体与轮廓 → 光与材质`.
- Preset `+ / - / 更新 / 重命名` clutter is collapsed into one outline overflow menu. Existing preset methods remain authoritative.
- **Motion** gains an `EXIT PREVIEW` stage with a Replay control. It provides a bounded, presentation-only indication of H70/H71 exit speed/flavor for fade, per-character, wipe, shrink, soft-drift, hop/drop, blur-decay, and instant. It never becomes a timing authority and never calls the real desktop exit lifecycle.
- Motion cards are ordered `退场 → 入场 → 运动 → 空间方向 → 同步` beneath the preview.

## Preview scope and performance

The preview is deliberately not another lyric engine. It draws only inside the control panel using existing Qt vector primitives and the existing soft-glow helper. The motion preview caps rendered sample text to 18 characters and updates at ~42 fps (24 ms) while replaying. Appearance preview repaints only when relevant controls change.

Blur preview is an **illustrative depth/defocus cue**, not a second implementation of H62-H72 Atlas blur. The actual desktop lyric remains the sole source of truth for production rendering.

## Compatibility

- Underlying tab indices remain H73-compatible.
- Existing H12 config keys (`h12_font_weight`, `h12_lyric_opacity`, cover-follow state) remain unchanged.
- Existing H70 profile controls remain the config owner; H74 only reads them for preview.
- No SVG/icon font/new package resource is added. H73/H74 icons remain dependency-free QPainter primitives.
- No threads, network calls, QImage raster filtering, player clock calls, provider calls, seek calls, or desktop lyric row mutations are added by H74.

## Historical replay boundary maintenance

During the full H74 canonical replay, two historical gates were found to use `__main__` as an open-ended extraction boundary. That made unrelated later UI generations part of their minimal fake-runtime snippets once H74 introduced `QFrame` at module scope. The runtime source was not changed for these findings.

- `CHECK_AUTO_PRECISION_DEADLINE_H14_REPLAY.py` now reviews the H14 keep-fast ownership closure only up to the following H27 marker.
- `CHECK_REFERENCE_NATIVE_CONTINUITY_H31_REPLAY.py` now reviews the H31 continuity closure only up to the following H35 marker.

Both gates retain their original functional assertions and pass after the boundary correction. These are test-generation ownership fixes, not H74 product behavior changes.
