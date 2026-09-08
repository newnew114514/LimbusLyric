# H9 Auto-Track Provisional Transport Closure

## Reproduced field symptom

A QQ automatic track switch could confirm a new identity while the selected GSMTC session briefly published `unknown`. The existing auto-local renderer clock was created, but because it inherited `unknown`, it remained at 0 until a validated QQ time pair arrived. In the captured field log this produced a hard handoff from 0 to about 8.42 seconds.

## Runtime change

H9 records only explicit transport observations from the selected player's real GSMTC/native/Bridge transport path, together with player identity epoch. On a confirmed different-song auto bind for QQ or NetEase, a fresh PLAYING observation from the immediately previous identity epoch may arm a bounded display-only carry through transient UNKNOWN status.

The carry:

- never writes UIA/GSMTC/seek/provider authority;
- is unavailable on startup late-attach;
- rejects stale, cross-player and cross-epoch evidence;
- is cancelled by explicit PLAYING, PAUSED or STOPPED;
- freezes on PAUSED/STOPPED;
- expires after 12 seconds if no real transport evidence arrives;
- does not apply to KuGou, whose H7 rail-local authority remains the source of truth.

## Release replay

`installer/CHECK_AUTO_TRACK_PROVISIONAL_TRANSPORT_REPLAY.py` uses the production methods and a deterministic monotonic clock. It proves the 8.4-second QQ UNKNOWN interval advances to roughly 8.4 seconds instead of staying at zero, while all veto/expiry/isolation cases remain safe.

## Deliberately not changed

QQ's approximately 1.8-second duration/version verification window is retained. H9 fixes the transport/display state-machine defect without simultaneously loosening same-title lyric-version filtering.
