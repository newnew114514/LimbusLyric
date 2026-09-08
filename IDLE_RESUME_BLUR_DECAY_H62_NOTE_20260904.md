# H62 — Idle Resume Continuity + Progressive Blur-Decay Exit

Date: 2026-09-04

## Field evidence

H61 field logs reproduced a deterministic presentation discontinuity at the end of long provider-confirmed lyric gaps. During the gap, the current row was correctly released into fading and QQ capacity residency explicitly retained two historical rows (`held=2`, `emergency_dropped=0`). When the first lyric after the gap arrived, `full_text` was intentionally empty because the suppressed row had already been released. The generic first-locate/reload branch therefore cleared `history_lines` and `fading_lines` even though the timeline transition was the normal suppressed-line -> next-line forward resume. The visible stack changed from held history/fading to a single new row without any exit animation.

## H62 continuity fix

`LyricWindow.check_lyric_time` now captures the provider-idle suppressed line before clearing the suppression marker. A non-seek forward transition from exactly that suppressed line to its next lyric is treated as an idle-gap resume presentation handoff. Existing held/fading rows are preserved; ordinary first locate/reload and seek behavior remain unchanged. Normal capacity residency subsequently releases the oldest held row through the selected exit effect instead of clearing the stack.

Diagnostic: `H62空白段恢复保留驻留字幕`.

## New exit effect: 渐进失焦 / 模糊退场

The effect is residence-age driven instead of a one-shot opacity animation. A completed row starts an age clock when it becomes a held history row. As it remains visible, its material is progressively low-pass filtered; after the later part of the progression its visibility also falls smoothly to zero. If capacity releases the row before natural expiry, the current blur progress is preserved and the remaining progression accelerates rather than restarting from sharp.

The optical source is H57's immutable birth material. Therefore text, outline, shadow, Glow and fixed random Z-depth are already baked together before H62 adds age defocus. With 3D depth enabled, the model is additive: `birth depth defocus + residence-age defocus`. A deep row starts soft and becomes softer; a foreground row starts sharp and gradually defocuses. H62 never replaces the depth assignment.

## Performance and continuity rules

- No blur rasterization is performed from `FadingLine.draw` or the paint hot path.
- The GUI thread snapshots the authoritative material to `QImage`; a daemon `LimbusLyric-H62BlurDecay` worker builds medium and maximum low-pass stages.
- Worker results return through the existing queued atlas-ready signal; `QPixmap` creation is GUI-side only.
- Worker budget is bounded. Missing/failed blur stages fall back toward the authoritative birth material rather than blocking paint.
- H59 first-visible-frame continuity also applies to H62's own accelerated release clock. A stall immediately after capacity release cannot advance the effect from visible to dead before one released frame is painted.
- Switching an already-visible row from another exit effect to blur-decay restarts its H62 age at the moment of selection. It never inherits a hidden age clock from row construction.

## Scope

H62 is presentation-only except for the narrow, evidence-backed idle-resume branch in `check_lyric_time`. It does not alter player clocks, seek authority, automatic lyric transactions, provider ownership or track identity.
