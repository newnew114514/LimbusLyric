# H41 Multi-provider state authority + lyric completeness

H41 is based on the Win10 H40 field session and the legacy `fake town baby` NetEase report.

- QQ: a valid monotonically moving GSMTC Position with `PlaybackStatus=unknown` is now a presentation/duration witness after coherent motion proof. It cannot grant Seek authority. The first bind after switching *to* QQ may seed presentation from the already selected QQ session position, avoiding a fake 0s start.
- NetEase: accepted duration-reconciled payload metadata is committed before the historical result transaction clears its key, closing repeated H38 refetch loops.
- KuGou Win10: `visual-rail-auto` cannot create an absolute local clock while player duration is still unowned. Short physical rail fragments are retained across visual-state resets for duration consensus. A fresh GSMTC identity prevents a stale Host-V2 title from immediately reverting the just-bound track.
- Semantic lyric-mode refetches preserve the current media clock epoch; artist enrichment cannot reset playback to zero.
- Cross-provider precise lyrics on long songs must have a minimally plausible timeline. A 263s payload with only six events ending around 5s is rejected and alternate complete candidates are tried. This targets the `fake town baby` regression without imposing a high line-count requirement on legitimately sparse songs.
