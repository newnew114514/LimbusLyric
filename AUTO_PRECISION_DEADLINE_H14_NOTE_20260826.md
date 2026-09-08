# AUTO PRECISION DEADLINE H14 — 2026-08-26

## Evidence
A real H10F4 user log (`LimbusLyric_20260826-153946_pid3808.log`) showed KuGou auto-track progressive lyrics for `worry (Slowed)` displaying ordinary LRC at about 2.2s, while the background precise/KRC enhancement did not finish until about 204.8s later. The result was correctly generation-rejected after the track changed, but the old enhancement task remained alive far too long.

The same trace contains artist enrichment (`LONOWN -> LONOWN、Riserayss`). In that path `search_kugou()` may ask `LyricFetcher.get_kugou_ui_duration_hint()` for same-title version evidence. That helper walks KuGou MSAA/COM accessibility nodes and historically had no deadline, making it a stronger suspect than the already bounded HTTP calls.

## H14 closure
H14 is a lyric-retrieval responsiveness closure only. It does not change KuGou transport/seek/HostV2 authority, QQ Software-2, NetEase native timing, V28/V29 presentation/transport contracts, or H11-H13 behavior.

1. Automatic KuGou precise enhancement gets a 22s cooperative total budget. The budget applies only when the current thread is an `LimbusLyric-AutoLyrics-g*` worker, source is KuGou, precise mode is requested, and translation-only is off.
2. At most two automatic KuGou precise enhancements may be in flight. A third request skips provider work immediately and keeps the already-visible fast lyric.
3. The KuGou MSAA version-duration hint is separately isolated on a daemon worker and gets a 1.25s wait budget during automatic precise enhancement. Only one such potentially stuck hint probe may exist at once.
4. If the MSAA hint times out or its slot is already occupied, the precise result is considered version-unproven and is discarded even if a later KRC/network payload returns. The ordinary fast lyric remains presentation owner.
5. A timed-out/saturated precise pass never writes the returned payload into the auto lyric cache and never rebinds MediaSync.
6. `progressive_keep_fast` is accepted only when the current loaded track is actually the same song. A duration-rejected fast candidate that was never displayed cannot masquerade as an already-visible fast lyric.
7. Manual lyric fetch remains under H11's independent async/GUI budget and is not changed by H14.

## Fault injection
`installer/CHECK_AUTO_PRECISION_DEADLINE_H14_REPLAY.py` executes the H14 outer closure without Qt and verifies:
- non-auto, fast-stage, and NetEase searches pass through unchanged;
- a cooperative slow KuGou precise search closes at the injected replay budget and returns no precise payload;
- parent generation cancellation remains authoritative and is restored;
- two occupied precise slots make a third precise enhancement skip provider network immediately;
- a slow MSAA duration hint returns at its injected deadline and marks the precise pass unsafe;
- even a later precise-like payload is discarded after version-hint timeout;
- keep-fast is retained only when the fast stage actually owns the current presentation.

## Release rule
Run all canonical gates. H14 adds one dedicated gate; the canonical suite is 72 entries. Never weaken KuGou golden locks or regenerate source locks to hide an H14 regression.
