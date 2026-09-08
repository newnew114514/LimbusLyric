# H10F4 — QQ Post-Rail Trend Recovery

Scope: QQ seek recovery only. H10F3 burst-display UI behavior, H10/H10F1 player liveness, H10F2 startup display-seed guard, H9 provisional transport, KuGou H7 transport/pause authority, and H8 GUI hot-path isolation remain unchanged.

Observed host case (`LimbusLyric_20260820-225700_pid26292.log`, song `但`): after a physical QQ rail gesture the rail geometry estimate was around 2.6s, while the first validated UIA seek commit latched around 11.4s. The subsequent real compact Text stream restarted near 0s and advanced normally, but the existing 12.5s post-rail stale-stream veto treated it as a delayed old stream. Interleaved unrelated Text values (37s/42s/51s/120s) could further erase the trend, so the clock sometimes waited many seconds before a stable unarmed commit.

H10F4 keeps the existing 12.5s host-safe veto unchanged for ordinary rail commits. A recovery exception exists only when all of these are true:
- the current rail commit has a same-gesture physical rail hint recorded at the exact commit epoch;
- the UIA commit target and physical rail hint disagree by at least 4.2s;
- the candidate Text stream is duration-matched and remains plausibly near the physical rail timeline;
- while playing, at least three advancing samples form a wall-clock-like trend.

During that narrow recovery, at most two gross isolated Text outliers may be ignored without erasing the coherent main trend. Geometry never becomes playback-time authority: the committed time still comes from validated QQ Text. New rail gestures and existing explicit click/lyric evidence keep their prior paths.

Dedicated replay covers:
- geometry/UIA conflict `0 -> 1 -> [37 outlier] -> 2s` recovers around 2.42s within ~2s;
- original host-safe `51.420s rail -> delayed 54/55s old stream` remains quarantined with no pending evidence;
- unrelated far Text stream cannot use the exception;
- missing/stale rail geometry cannot use the exception.
