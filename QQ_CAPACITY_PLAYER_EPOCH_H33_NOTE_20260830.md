# H33 — QQ Capacity + Player Epoch Closure

Field basis: Win10 frozen and Win11 build 26100/source-run H31 logs.

## Fixes

- QQ now uses capacity residency not only for normal row transitions and provider-idle release, but also for the historical direct-landing-inside-provider-idle branch. Already-held history survives that branch up to `max_visible_subtitles`; the suppressed current row remains suppressed.
- Short automatic transport hints are stamped with selected player name plus `MediaSessionSync._media_player_epoch`. A hint from QQ is invalid immediately after switching to NetEase/KuGou, and vice versa.
- H32 KuGou hook+poll seek observation, NetEase native 2.0.6 position sanity and native track-edge continuity revocation remain unchanged.
- No new clock authority and no synthetic zero are introduced.

## Field issues closed

- Win11/26100 QQ could internally reach `live_count=3` but remained on legacy residency, so users could observe only short-lived/single-row presentation in sparse precise sections.
- A QQ fast-event hint could remain alive for its short TTL across a manual player change and label/accelerate the new player's generic candidate as QQ transport evidence.

## Regression contract

`installer/CHECK_QQ_CAPACITY_PLAYER_EPOCH_H33_REPLAY.py` replays both cases and verifies non-QQ behavior is unchanged.
