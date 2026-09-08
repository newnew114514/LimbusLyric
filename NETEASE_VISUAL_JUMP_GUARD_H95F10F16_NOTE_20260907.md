# H95F10F16 — NetEase shared-visual jump + precision handoff guard

## Field evidence

An older H50 Windows session showed NetEase H30 shared visual transport holding a coherent ~7–8 s rail, then publishing a different horizontal UI surface as 171.339 s for one physical sample before returning to ~8.1 s. The automatic lyric transaction itself had already armed, loaded, and displayed lyrics; the defect was a one-sample visual-clock takeover, not a failure to auto-read.

## Closure

H35 already requires a second coherent sample for a large same-track discontinuity from the native detector. H95F10F16 applies the same class of protection only to the final H30 NetEase shared-visual fallback.

- Explicit click/drag seek evidence remains immediate.
- A large same-track physical H30 jump without seek evidence is held on the last trusted trajectory.
- A second temporally coherent physical observation confirms a genuine keyboard/remote/external seek.
- A return to the previous trajectory cancels the pending discontinuity.
- H30 proof history is retained, but rejected candidates cannot replace its active anchor/local lease.

## Precision handoff freshness

The same field session had H30 already at ~7.5 s while V28 created its precision visual lease from renderer `_last_position_ms=0`. F16 refreshes that renderer field once from the existing final `LyricWindow._playback_position()` immediately before the mature V28 handoff, only when the source is NetEase. It does not create a clock or change the precise timeline.

## Ownership boundary

No changes to native/Bridge/GSMTC clock authority, seek detection, lyric providers, parsers, renderer, visual effects, or player identity. The patch only wraps `MediaSessionSync._h25_poll_netease_safe_visual_clock` after H30 and leaves all protected RC11 functions untouched.
