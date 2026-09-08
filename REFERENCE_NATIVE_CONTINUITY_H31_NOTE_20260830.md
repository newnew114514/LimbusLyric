# H31 — Reference Native + Continuity Clock

Reference reviewed: `LimbusLyricSimulator-main(3).zip` (2026-08-29).

## What the reference actually does
- No Win10/Win11 clock fork: the same Windows Fetcher model is used on both.
- NetEase: `netease-cloudmusic-detector` first; its lockfile resolves **2.0.6**.
- Native detector startup is asynchronous and allowed up to **20 seconds**.
- QQ: SMTC with a stall guard.
- KuGou: explicitly marks progress unsupported; this part is **not** copied because current LimbusLyric has stronger KuGou rail/seek support.
- When external progress becomes unavailable after a valid sample, the lyric window switches to an internal monotonic clock from the last valid position instead of freezing.

## H31 transplant
1. Pin NetEase native detector to 2.0.6 and allow 20s async initialization.
2. Preserve H30 visual transport as fallback while native startup is pending.
3. Add NetEase presentation-only continuity after a trusted native/Bridge/physical-visual/validated clock anchor.
4. Continuity is cleared on seek, track epoch, player epoch, or player death.
5. Cold start with no real anchor remains UNKNOWN; no synthetic 0ms is introduced.
6. QQ and KuGou clock authority rules are not weakened.
