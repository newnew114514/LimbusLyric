# H35 Baseline Reconciliation — 2026-08-31

## Why this is a reconciliation, not a rollback

The user-supplied H10F4 package is the known-good Win11 baseline. A structural comparison against H34 found that the current main source grew from roughly 40.8k to 50.3k lines, but the original core was not broadly rewritten: 914 functions/methods are shared, only 21 same-name base functions changed directly, and 263 functions were added as later compatibility/runtime layers. The safest repair is therefore to preserve reviewed Win10 fail-closed paths while restoring baseline invariants at the final runtime boundary.

## Confirmed regressions closed by H35

1. **Emergency renderer no longer destroys multi-subtitle presentation.** H11 may still disable atlas/vector/glow work when a frame/build exceeds the hard budget, but H35 cheaply draws resident history and fading rows as plain glyphs. `max_visible_subtitles` remains a user feature contract even under performance fallback.
2. **NetEase native Seek is no longer one-sample authority.** Native detector parsing and identity checks remain unchanged. H35 suppresses H31/H29-era immediate one-sample publication and requires a second temporally coherent sample before publishing a formal seek serial. A one-frame false jump stays on the last trusted trajectory.
3. **QQ instrumental first-attach duration deadlock receives a scoped rescue.** The old fast-instrumental branch intentionally refuses to promote a provider duration to transport authority. H35 does not reverse that rule. It completes duration only after the already-bound QQ identity, the lyric candidate duration, and two distinct QQ current/total UIA samples agree.
4. **KuGou existing-playback attach now forbids synthetic zero at the bottom seed function.** H34's player-switch intent is mirrored into MediaSessionSync and blocks `manual-zero-bootstrap`, `auto-track-bootstrap`, and `lazy-zero-bootstrap` until a real position/transport witness arrives. A genuine later transport edge may clear the latch.
5. **Win10 COM/GC crash path uses the existing playback-scoped GC guard by default.** On Windows builds below 22000, unless the user explicitly sets `LIMBUSLYRIC_PLAYBACK_GC_GUARD`, H35 enables the already-reviewed collect-before-playback / defer-cyclic-GC-until-stop mechanism. This targets the observed `Garbage-collecting -> comtypes Release/__del__ -> nativeEvent` crash without changing Win11 default behavior.
6. **Same-track duration completion accepts conservative artist aliases across providers.** If normalized track keys differ only because equivalent artist lists use `/`, `,`, `、`, `&`, etc., H35 reuses the existing `_same_track`/alias proof and completes duration against the already-bound media identity instead of resetting the track.
7. **Subtitle-capacity mutations are now attributable.** Any real `max_visible_subtitles` change logs old/new value plus the recent Python caller chain. H35 deliberately does not block a 3→1 change until logs prove whether it came from the UI slider, launch wiring, or another state path.

## What H35 deliberately does not do

- It does not remove H22-H34 Win10 fail-closed accessibility protections.
- It does not weaken H34 KuGou large-drift rejection.
- It does not make lyric-provider duration alone become playback authority.
- It does not force the user's subtitle count back to a guessed value.
- It does not claim VM/Win10 visual-rail behavior is fixed without real-machine validation.

## Regression evidence expected in new logs

- `H35紧急渲染保留多字幕`
- `H35网易云Seek候选暂缓` followed by `H35网易云Seek二次确认` only for a real discontinuity
- `H35 QQ纯音乐时长三方闭环`
- `H35酷狗既有播放假零阻断` / `...阻断解除`
- `H35同曲歌手分隔符兼容`
- `H35字幕容量变更追踪`

The H10F4 source remains a reference baseline, not a file-level replacement target. H35 keeps the later environment hardening but restores these baseline behavioral contracts at the final runtime layer.
