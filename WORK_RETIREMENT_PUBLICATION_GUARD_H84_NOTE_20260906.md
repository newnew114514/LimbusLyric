# H84 Work Retirement + Publication Guard — 2026-09-06

Scope is intentionally narrow. H84 does **not** enable the broader Codex single-slot WinRT async request model.

## Included

- Row-atlas work is bounded to visible rows plus the current timeline/style lookahead.
- Obsolete queued row material is retired after timeline/style changes; visible rows are prioritized.
- An active row worker cooperatively stops when its key is no longer wanted.
- `stop_lyric()` immediately clears queued/wanted row work and the H82 prewarm epoch.
- H82 prewarm identity is now `(timeline epoch, style signature)`, preventing A→B→A style switches from inheriting stale `seen` state.
- Each `MediaSessionSync._poll_loop` iteration captures `(media_player_epoch, process_hint)`. After potentially slow media metadata reads, before shared UIA merge, and before final state mutation/publication, H84 rejects work whose owner no longer matches.
- `_set_state(_poll_owner=...)` is the final publication barrier, including ABA player switches where the process name returns to an older value under a newer epoch.

## Explicitly deferred

- Codex `_poll_owned_media_request` / manager + metadata single-slot async conversion. The design remains valuable but needs stronger shutdown/quarantine semantics for truly cancellation-resistant WinRT awaitables.
- No QQ/KuGou/NetEase/Spotify seek, clock selection, duration authority, or lyric-provider algorithm is intentionally changed.
- No packaging script is changed.
