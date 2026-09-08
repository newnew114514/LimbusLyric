# H44 Runtime Latency + Visual Quality Recovery

## Field evidence

Two affected-user reports exposed regressions that were not synthetic test failures.

1. On Windows build 26200, KuGou `A Rusty Dream` entered `playing` at 15:53:01 while GSMTC remained zero. The first positive HostV2 Slider sample (1870 ms) appeared at 15:53:18, but H43's 2200 ms display threshold rejected it; display did not unlock until a later 15680 ms sample at 15:53:35.
2. On a separate 240 Hz system, the configured lyric colors remained `text=#00ffff / glow=#00aaff`, but a worker song-atlas build crossed the 850 ms budget. H11 then permanently selected the plain-glyph emergency lane (`glow/vector=skip`, cadence <=60 Hz), changing apparent color/glow and making shake look choppy even though subsequent GUI paint was healthy.
3. The same user showed a NetEase H38/H41 reconcile storm. A new native identity/duration was combined with the old loaded payload identity, and H41 cleared H38's 12-second reconcile signature after every accepted result. This repeatedly reloaded stale cached lyrics and rebuilt presentation state.

## H44 policy

- New KuGou identities confirmed during the running app may use a non-absolute, display-only local clock while status is `playing`; startup-existing attach is excluded.
- First positive, identity-bound HostV2 Slider samples >=120 ms may calibrate that display clock. Exact zero remains quarantined; duration and seek authority are unchanged.
- NetEase version reconciliation is same-native-identity only. A new native track vetoes reconciliation of the old payload. Conflicting NetEase cache entries are removed before a duration-anchored refetch; stale async results are ignored; an unsuccessful same-identity refetch preserves H38 debounce.
- A `build-budget>` Atlas worker fuse disables further Atlas construction but does not imply slow GUI painting. Normal sprite/vector rendering and the configured visual cadence resume after worker completion. `paint-hard-budget` and GUI-install fuses retain the emergency renderer.

## Non-goals

H44 does not change configured lyric colors, QQ clock authority, NetEase native clock proof, KuGou formal seek authority, or H42's Host-zero quarantine.
