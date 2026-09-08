# Stabilization Core S1

## Goal
S1 starts reducing runtime coupling without rewriting the mature player/seek/clock stack. It is intentionally additive at stable boundaries: pure lyric data/normalization first, renderer admission second.

## Changes
1. Added `limbus_core/`, a dependency-free Python package with no Qt, Win32, COM, player, or network imports.
   - `lyric_model.py`: provider-neutral unified lyric track conversion and derived Unicode grapheme timing.
   - `search_policy.py`: deterministic duration/provider/bilingual candidate helpers.
   - `local_lyrics.py`: local LRC, YRC, KRC, QRC, WebVTT and TTML normalization into the existing Enhanced-LRC host contract.
2. H95 unified-lyric shadow construction now delegates to `limbus_core.lyric_model` when available and retains the previous H95 implementation as a fail-safe fallback.
3. Added a first-class **导入歌词文件** action beside the manual lyric editor. Local import does not change player identity or transport ownership. Precise material uses the existing seamless timeline handoff when playback is already active.
4. Added a bounded slow-paint anti-cascade latch. A late paint temporarily suppresses only speculative renderer work (priority > 1); visible/current material (priority <= 1) is always admitted.
5. Existing duration compatibility behavior is delegated to the pure search-policy helper with the previous implementation retained as fallback.

## Local lyric compatibility
- LRC / Enhanced-LRC: direct.
- YRC: word timing normalization.
- KRC: plaintext and standard local `krc1` XOR+zlib payloads.
- QRC: plaintext / XML `LyricContent` forms. Proprietary encrypted binary QRC is not claimed by S1.
- WebVTT: cue timing and inline timestamp timing.
- TTML/XML: line timing plus nested leaf timed spans; intentional inter-word whitespace is preserved.

## Protected authorities
S1 does **not** change QQ/KuGou/NetEase/Spotify player identity selection, GSMTC/UIA/MSAA/native clock ownership, seek authority, track-epoch rules, provider network requests, or mature entrance/exit effect-progress formulas.

## Validation performed in the source environment
- Pure-core grapheme/model/normalizer/policy regression samples: PASS.
- Python compile of the changed source/modules: PASS.
- Existing targeted replays observed PASS for lyric precision visual handoff, multi-provider state authority/lyric completeness, lyric identity firewall, render hot-path/UI coherence, payload firewall/high refresh, unified lyric visual-timing facade, render snapshot/perf contract, shared render-work scheduler, and H95F10F17 exit-material continuity/multi-row budget.
- Packaging contract was observed PASS before final manifest refresh.

A full Windows field run against live QQ Music, KuGou, NetEase Cloud Music and Spotify was not performed in this environment. Those integrations remain protected legacy authorities and should be field-tested on the target Windows versions before treating S1 as a production release.
