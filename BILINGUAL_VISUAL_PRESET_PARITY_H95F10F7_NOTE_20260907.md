# H95F10F7 — Bilingual Visual Preset Parity

Scope: presentation only. Provider clocks, seek, parsers, primary lyric rendering and player transport remain unchanged.

- Translation entrance now executes the mature ordinary-LRC visual state rather than the copied F4 envelope.
- Translation typography executes H51 through a secondary-lane proxy; F4 no longer owns a copied font/script resolver at runtime.
- Per-character/wipe exits reuse the existing primary glyph-state kernel; group exits reuse the existing group transform; blur remains H62/H69-owned through F6.
- Music-reactive glyph scaling shares the one primary audio monitor, thresholds, confirmation hold and upward-only growth; no second sampler exists.
- Translation now participates in device-space horizontal wrap and keeps primary perspective -> anchor -> fixed-Z history transform order.
- Cached sprites remain the final paint material; no QPainterPath or image filtering is introduced into translation paint.

Known boundary: H57's precomposited Defocus/Bloom birth material is still primary-lane-only. F7 mirrors fixed-Z/perspective geometry but deliberately does not synthesize a second H57 optical atlas in paint. This is retained as an explicit low-priority parity gap rather than reintroducing frame stalls.

## Final optical parity closure (2026-09-07)

The final F7 closure also removes the remaining H57 optical-material gap. The bilingual
translation lane now prepares its immutable birth-depth material from already-cached high-DPI
glyph sprites only. GUI work is limited to snapshot/install; Defocus/Bloom filtering and
compositing use QImage in a background worker. A missing cached glyph delays the material build
rather than rasterizing from paint or the depth prewarm callback.

When `blur_decay` is selected, H62/H69 remain the lifecycle/progress authority, but their base
material is the translated H57 birth-depth atlas when depth is enabled. Thus depth no longer
sharpens or changes optical identity when the translated row enters blur decay. If the async
material is not ready, rendering remains on the ordinary cached-sprite fallback; there is no
multi-tap fake blur or synchronous depth construction.
