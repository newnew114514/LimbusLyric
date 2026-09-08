# H95F10F5 — QQ auto-track stale rollback guard

## Field evidence
An H10F4 field log showed a real QQ publication-order race, not a failure to start auto lyric search:

1. `qq-gsmtc-fast-event` published the new identity (`mede:mede` / Reol).
2. LimbusLyric immediately started a provisional new-track transaction and reset MediaSync to that identity.
3. For about one second, QQ's ordinary media snapshot/UIA clock still described the previous track (`Flower of Life`, ~341.9 s).
4. The normal detector briefly returned that still-loaded old identity and the suspended old lyric payload was restored.
5. The new-song provider search continued/finally failed, but presentation ownership had already been stolen back by the old snapshot.

The symptom can therefore look like “切歌后没有主动读词/没有自动开始”, even though search did start.

## Fix
H95F10F5 adds a presentation-only rollback guard around the final cached-old-track restore owner.

For QQ only, restore is blocked when all of these are true:

- an old payload is currently suspended by a confirmed new-track transaction;
- `_auto_target_key` differs from `_loaded_track_key`;
- the detector is asking to restore exactly the loaded old identity;
- the freshest QQ background fast-identity key is exactly the pending target;
- that fast-identity publication is <= 2600 ms old.

After the short publication-lag window expires, or when there is no pending/fresh target, the historical restore path is unchanged. This preserves a genuine rapid return to the old song while preventing the specific stale-snapshot rollback shown in the field log.

## Ownership boundary
The patch does **not** modify:

- `MediaSessionSync` clocks, seek, bind, player epochs, or UIA/GSMTC polling;
- `_monitor_track_change` detector logic;
- `_request_auto_track` or lyric provider/network search;
- parser, renderer, bilingual, cover, or packaging behavior.

## Gate
`CHECK_QQ_AUTOTRACK_ROLLBACK_GUARD_H95F10F5_REPLAY.py` replays the exact ownership predicate and verifies both sides:

- fresh new QQ target + stale loaded snapshot => restore blocked;
- guard expired / genuine old-track return => historical restore delegated.
