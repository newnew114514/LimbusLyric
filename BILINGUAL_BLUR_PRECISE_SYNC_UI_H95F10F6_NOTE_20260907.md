# H95F10F6 — Bilingual blur parity, precise recovery, sync UI cleanup

Field log review on 2026-09-07 identified four separate issues that should not be conflated:

1. **Bilingual blur-decay did not use the mature blur material renderer.** H95F10F4 simulated blur by drawing each translation glyph five times. That multiplied draw cost and made the secondary lane look fully blurred too early. H95F10F6 builds translation blur materials asynchronously with the existing H62 low-pass pipeline and renders base/mid/max materials in batches using the same H62 decay clock/mix as the primary lane. Until the material is ready, one clear cached-sprite pass is used; the five-tap approximation is never used by the final owner.
2. **Low-quality ordinary LRC could poison the precise cache.** The progressive worker historically cached any non-empty `prefer_precise=True` result in the precise namespace. A provider fallback that returned ordinary LRC could therefore suppress future QRC/KRC retries. H95F10F6 purges historical soft precise entries and treats an ordinary fallback on the progressive auto worker as an enhancement miss. Instrumental terminal payloads remain valid.
3. **QQ candidate→validated duration labels could restart stability at the wrong moment.** The protected resolver remains byte-identical. If all historical resolution layers return zero, H95F10F6 gives QQ a narrow 220 ms second chance where the same duration across `qq-time-pair-candidate` and `qq-time-pair-validated` is continuous evidence, while old/pre-bind durations remain rejected.
4. **Advanced Sync Doctor controls crowded the normal sync card.** The current-player offset remains visible. The expert ±50/100 ms, anchor and drift controls are preserved behind a collapsed `高级同步校准` disclosure by default.

The patch deliberately does **not** alter MediaSessionSync clock/seek authority, parser ownership, provider identity rules, or the primary precise/classic renderer.
