# Stabilization Contract S2

## Intent
S2 continues the S1 migration without a flag-day rewrite. The mature QQ/KuGou/NetEase/Spotify clock and seek stack remains the field fallback, but new code no longer has to know provider-specific search signatures or arbitrary playback dictionaries.

## Runtime contracts
1. `limbus_core/provider_runtime.py`
   - `LyricQuery`: one provider-neutral acquisition request.
   - `LyricProviderResult`: one result shape with payload provenance and metadata.
   - `ProviderRegistry`: runtime provider dispatch for NetEase / QQ Music / KuGou.
   - Provider method lookup is dynamic, so the mature H95F8 safety guards still wrap the actual network provider methods.
   - The base search coordinator and H95F10F8 precise bilingual rescue use the registry first and fail open to the legacy direct dispatch if the new glue itself faults.
2. `limbus_core/playback_model.py`
   - `PlaybackSnapshot` normalizes the established `MediaSessionSync.snapshot()` dictionary without choosing a new clock owner.
   - Unknown diagnostic/evidence keys are preserved in `extras` and round-trip through `to_legacy()`.
   - `MediaSessionSync.contract_snapshot()` is additive; the mature `snapshot()` function is not replaced.
3. `limbus_core/fault_journal.py`
   - bounded 96-row in-memory exception journal for newly refactored boundaries;
   - uncaught Python thread/unraisable exceptions are observed in addition to the existing session logger;
   - existing caught exception behavior elsewhere is intentionally unchanged in S2.

## Search-policy consolidation
- S1 duration/provider ordering helpers are now used inside the mature search coordinator where replay-safe.
- H95F10F8 precise bilingual pair ranking delegates to the pure policy helper, with the original local ranking retained as fallback.
- Provider-specific network/parsing implementations remain in `LyricSearchEngine` for now; S2 moves the *dispatch contract*, not the field-proven HTTP code.

## Patch-debt freeze
S2 adds `CHECK_PATCH_DEBT_BUDGET_S2.py`. These existing hotspots may be reduced but must not gain another direct runtime layer:

| Hotspot | S2 budget |
| --- | ---: |
| `LyricSearchEngine.search` | 5 |
| `MediaSessionSync.snapshot` | 4 |
| `MediaSessionSync.bind_track` | 6 |
| `LyricWindow.paintEvent` | 10 |
| `ControlPanel.__init__` | 54 |
| `ControlPanel._on_auto_lyric_result` | 14 |
| `LyricWindow._make_history_line` | 18 |
| `FadingLine.draw` | 17 |

The numbers are intentionally not presented as healthy. They are a frozen migration baseline. Future work on these methods must consolidate/delete an old layer before adding another.

## Protected behavior
S2 does not intentionally change player identity selection, GSMTC/UIA/MSAA/native clock authority, seek authorization, track epoch rules, lyric animation/effect progress, or renderer material formulas.

## Validation in this environment
- S2 pure contract gate: PASS.
- Runtime Search Chain H95F10F1: PASS.
- Multi-provider State Authority / Lyric Completeness H41: PASS.
- Lyric Identity Firewall H81: PASS.
- Bilingual Blur / Precise Cache / Sync UI H95F10F6: PASS.
- Sync UI / Cold Render / Precise Pair Priority H95F10F8: PASS.
- Unified Lyric / Visual Timing Facade H95F10F12: PASS.
- Render Snapshot / Performance Contract H95F10F13: PASS.
- Shared Render Work Scheduler H95F10F14: PASS.
- Exit Material Continuity / Multirow Budget H95F10F17: PASS.
- Lyric Pipeline V28 Precision Visual Handoff: PASS.

Live Windows player testing is still required before treating S2 as the new production baseline.
