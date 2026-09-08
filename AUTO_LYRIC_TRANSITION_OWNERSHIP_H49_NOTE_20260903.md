# H49 automatic lyric transition ownership recovery

Field evidence from the 2026-09-03 NetEase sessions shows a deterministic race in H44:

- a real native `track_serial` edge starts a new provisional auto-track transaction;
- the new song's lyric result can finish before the native title/artist lane leaves the previous song;
- H44 compared the correct new result against that still-old native identity and rejected it as stale;
- because the H44 veto returned before the historical result handler, `_auto_fetch_in_progress` stayed true;
- later manual lyric requests were coalesced into a transaction that had already been discarded.

H49 keeps H44 fail-closed behavior but distinguishes a lagging old native identity from a genuinely stale/misparsed result. A mismatching NetEase result may pass only when all of the following are true:

1. it is the current generation/source/target transaction;
2. MediaSync is already provisionally bound to that same target key;
3. the mismatching native identity still matches the currently loaded old lyric payload;
4. a real NetEase native `track_serial` edge occurred recently and the provisional bind belongs to that edge.

If a mismatching result is current but does not satisfy those proofs, H49 keeps H44's rejection and explicitly releases the auto transaction so the next stable observation can retry. Old/non-current results remain untouched and cannot clear a newer in-flight job.

Regression: `python installer/CHECK_AUTO_LYRIC_TRANSITION_OWNERSHIP_H49_REPLAY.py <main.py>`.
