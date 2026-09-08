# H37 Runtime Reconciliation + UI Recovery

This layer is based on the 2026-08-31 Win11 host and Win10 frozen test logs. It intentionally keeps H22-H36 provider/COM safety policy and closes only observed interaction gaps.

## Changes

- Emergency renderer: retained history/fading rows now consume their live `char_shakes` and `glyph_scales`, so an atlas fuse no longer turns old subtitles into visually frozen text. Glow/vector work remains disabled in emergency mode.
- Win10 KuGou seek: user seek geometry is derived from the cached HostV2 rectangle (`x=3.5%..96.5%`, `y=89.5%`) and is independent of visual-rail clock geometry. The low-level mouse hook only accepts a narrow rail band on the frozen Win10 safety profile; unrelated lower-window clicks cannot teach a fake rail.
- Win11 QQ background: a recent minimized/off-screen window followed by a 1.8-10s backward, evidence-free UIA stream cannot be promoted to an unarmed seek. Click/lyric-backed and large seeks are unchanged.
- Win10 liveness: after a corroborated negative, expensive negative process discovery backs off for 8s while PSAPI positive checks remain immediate, reducing repeated VM churn.
- Control panel: titlebar buttons return to compact boxed controls with balanced `−`, `▢/❐`, and `×` glyphs.

## Explicit non-changes

- H35 Win10 playback GC/COM guard remains enabled.
- NetEase native two-sample seek confirmation remains unchanged.
- QQ normal rail seek/session commit path remains unchanged.
- KuGou visual clock large-drift authority remains governed by H36.
