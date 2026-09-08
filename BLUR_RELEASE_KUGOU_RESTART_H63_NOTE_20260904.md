# H63 · Blur-decay release + KuGou same-track restart display closure

## Field evidence

H62 introduced an age-driven `blur_decay` exit. A real H62 log with three resident subtitles showed `history_count=2` staying bounded while `fading_count` climbed from 1 to 10 and `visual_count` reached 13. The emergency fade-lane valve could only drop one row as each new row arrived, so paint cost kept growing.

The lifecycle defect was narrower than the blur model itself. `h62_draw()` correctly increments `_h62_decay_release_draw_count` after its composite Atlas path, but when the authoritative H57 birth material is temporarily unavailable it falls back to the mature renderer and returns early. That fallback is visibly painted, yet H62 never records the visible release frame. `_h62_decay_progress()` therefore keeps applying H59's pre-first-frame 120 ms catch-up cap forever and the released row never reaches progress 1.0.

A separate frozen-Windows KuGou H51 log did not show a stale previous-song lyric payload being applied after track ownership changed. It showed a same-track restart display-clock race: `Hero|Mili` remained the loaded/host identity, the old visual rail was near 198.8 s, while HostV2 had already cached a fresh Slider sample near 7.37 s. Explicit Start rendered the end-of-song line once before HostV2 re-anchored the display to ~8.3 s.

## H63 closure

1. Any completed `FadingLine.draw()` for `blur_decay` satisfies the H62 visible-release-frame contract. If H62's composite path already increments the counters, H63 does nothing; if H62 returned through fallback, H63 fills only the missing draw/release count. The 120 ms first-frame guard therefore remains intact without becoming a permanent lifetime lock.
2. Membership in `LyricWindow.fading_lines` is authoritative release ownership. A `blur_decay` row directly appended by a legacy snapshot producer is idempotently promoted through `begin_fade()` before `update_fading()`; it cannot accidentally spend the 6.5–18 s history-hold duration in the exit lane.
3. On an explicit KuGou user Start only, H63 may use a recent cached HostV2 Slider/ProgressBar candidate to repair a very large backwards disagreement with the same-track local display rail. Track key and player epoch must already match; evidence must be fresh; the correction is seeded with `absolute=False` and is display-only. H63 does not bind a track, change duration, publish seek authority, or monkeypatch `MediaSessionSync` methods.

## Preserved behavior

- H62 provider-idle resume continuity remains unchanged.
- H62 async residence blur and H57/H58 depth/style material remain unchanged.
- H59 first-visible-frame protection remains active.
- Classic exit effects remain untouched.
- H27/H28/H34/H43/H44 KuGou track/transport ownership remains the authority; H63 only closes the explicit-Start presentation race using already-observed HostV2 evidence.
