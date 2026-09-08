# H95F10F1 Runtime Search Chain + Fallback Transaction Closure

## Field regression
A Windows field log from H95F10 showed every QQ auto-track result closing as `ok=0`, `duration=0`, `elapsed=0ms`, followed by `QQ自动歌词失败事务解锁` and a later `自动歌词搜索过期结果丢弃` with an empty `current_key`.

## Confirmed root cause
The final runtime lyric-search chain is H95F8 -> H41 -> H14 -> base search. H95F8 forwards the H95F10 source-lock keyword arguments `provider_locked` and `require_translation_pair`, but the intermediate H41 wrapper still exposed the historical signature. Python therefore raised `TypeError` before a provider request began. The auto worker converted that exception into a normal empty result, which made the field failure look like a zero-millisecond provider miss instead of a runtime-call regression.

## Fixes
- H41 now accepts both source-lock keyword arguments and forwards them only when active, preserving the historical call shape for old adapters.
- H41 does not perform its historical cross-provider completeness replacement when a bilingual pair or provider-locked sidecar is active; this prevents H41 from silently breaking H95F10's same-provider invariant.
- Auto-search worker exceptions are explicitly logged as `自动歌词搜索异常` before the failure result is emitted.
- H94 auto fallback now owns a pending target key while its fourth-provider lyric-only worker is active.
- The separate QQ failure cleanup slot defers target release while H94 owns that fallback.
- H94 treats an empty current target key as stale ownership, preventing late fallback resurrection after a real release.

## Regression coverage
`CHECK_RUNTIME_SEARCH_CHAIN_H95F10F1_REPLAY.py` reproduces the production H95F8 -> H41 call shape, checks ordinary backward compatibility, verifies bilingual/provider-locked forwarding, and asserts the H94/QQ transaction-ownership closure.
