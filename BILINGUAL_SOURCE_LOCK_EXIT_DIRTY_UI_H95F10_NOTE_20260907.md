# H95F10 — Bilingual source lock, exit dirty closure, and UI stability

## Scope

This patch is deliberately bounded to bilingual lyric provenance/presentation and frontend shell behavior. It does **not** change MediaSessionSync clock/seek ownership, player-specific transport logic, parser ownership, or the established H72/H95F6 exit timing model.

## Audit findings

1. Bilingual translation was a late sidecar request. The main lyric could be loaded first and `_h95f5_schedule_translation_fetch` could later call `LyricSearchEngine.search(..., trans_only=True)` independently.
2. Translation-only search historically allowed safe cross-provider borrowing. That meant main lyric provider A and translation provider B could coexist even when the selected bilingual intent was “one coherent provider pair.”
3. Translation cache identity was title/artist based (plus duration guard) but did not reject a cached translation when the displayed main lyric payload source changed for the same song.
4. H72 terminal dirty cleanup predates the bilingual lane. The final retirement helper could clear the main lyric envelope while omitting the later translation lane, leaving stale translation pixels until a larger/full invalidation.
5. The modern top title material had alpha values around 60% black, visually closer to opaque than the requested ~40–50% black.
6. The pre-first-row sync badge exposed transient synchronization arbitration. During player attach/duration settling this could change repeatedly before any lyric row was actually displayable.
7. H95F3/H95F4 UI replay contracts still expected descriptive frontend names instead of the requested exact `新版` / `旧版` labels.

## Changes

### One-provider bilingual pair

`LyricSearchEngine.search` now accepts `require_translation_pair` and `provider_locked` policies.

When live bilingual mode requests a main payload, the search evaluates providers as **whole pairs**: a candidate is eligible only when that provider supplies both a usable main lyric and a normalized translation for the same safely matched recording. Candidate selection prefers translation coverage, then timing quality, then the user's preferred provider on ties. To avoid turning every normal bilingual lookup into three serial provider requests, a preferred-provider pair with at least 90% translation-row coverage is accepted without probing foreign providers; foreign probing is reserved for missing or materially incomplete translation. Once selected, the normal cross-provider main-lyric quality ladder is not allowed to replace only one half of the pair.

If the preferred provider has lyrics but no translation and another safely matched provider has both, the other provider supplies **both** displayed main lyric and translation. If no provider has a safe pair, the main lyric remains available but translation stays missing rather than silently mixing providers.

The translation sidecar now locks to the actual `lyric_payload_source`, disables cross-provider translation borrowing, and rejects cache rows whose provider differs from the current main payload provider. The exact translation validated during pair selection is also handed off through a bounded in-memory pair cache, so the sidecar normally reuses that exact payload instead of immediately making a second network request; provider-locked re-fetch remains only as a fallback for persisted-cache/restart cases.

Auto-lyric cache keys now separate bilingual-pair transactions from ordinary transactions so a previous non-bilingual cache entry cannot bypass pair selection.

### Translation exit continuity

H95F10 extends the exact `_h72_held_visual_region` terminal retirement helper used by H72. The translation lane's last dirty region is unioned into H72's terminal clear envelope. This preserves the existing exit effect/timing while preventing stale translation pixels from surviving after the main row retires.

### Frontend shell

- Frontend selectors now use exact labels `新版` and `旧版`.
- Modern titlebar black alpha is `122` / `116` (~48% / ~45%).
- Before the first actual lyric row appears, the sync badge uses stable semantic text (`读取中` / `等待歌词`, plus paused suffix) and bounded width instead of exposing transient source arbitration labels.

## Regression contract

`CHECK_BILINGUAL_SOURCE_LOCK_EXIT_DIRTY_UI_H95F10_REPLAY.py` protects:

- provider-pair selection and provider-locked translation sidecar;
- source-aware translation cache invalidation;
- bilingual auto-cache namespace isolation;
- H72 terminal dirty-region inclusion of translation;
- stable pre-first-row sync badge;
- exact `新版` / `旧版` naming and ~40–50% title material alpha;
- no H95F10 clock/seek/parser authority takeover.

Existing H95F3/H95F4/H95F7 replay expectations were updated only where the requested UI contract changed.

## Full-gate audit closure

The first complete 172-gate pass exposed two additional compatibility hazards and one stale gate contract; these were corrected before release packaging:

- H14 and H95F8 both wrap `LyricSearchEngine.search`. Their legacy signatures initially did not accept the new `provider_locked` / `require_translation_pair` policies, which could make real auto/manual bilingual calls fail at the final runtime wrapper even though an isolated base-search replay passed. Both wrappers now accept and forward the policies. H14 preserves the old call shape when neither policy is active so older/injected search adapters remain compatible in ordinary mode.
- The first bilingual cache namespace draft inserted a tuple field and shifted historical positional indexes. H28/H38/H81 cache-safety layers rely on `[3]` as track identity and `[-1]` as QQ/KuGou duration. The final design keeps tuple length/indexes unchanged and uses the existing trans-only namespace slot as the `bilingual-pair` discriminator, preserving those purge/version-safety contracts.
- The H94 replay originally scoped its “do not replace search authority” assertion from the H94 marker all the way to process entry. That became stale after the later H95 family added its own guarded wrappers. The gate is now correctly scoped to H94/H94F1 only; H95 wrapper authority is separately covered by H95F8/H95F10 gates.
