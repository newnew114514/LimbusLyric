# H19 Cover Follow + Mirrored Exit (2026-08-28)

Real-machine H18 logs exposed two presentation defects that static H16/H17 replays did not reproduce.

## Cover-follow

The NetEase legacy web-search payload commonly contains `album.picId` but not `album.picUrl`. H16 treated `album.picUrl` as mandatory, so valid song matches repeatedly ended in `cover-not-found` and the configured lyric color never changed.

H19 keeps H17's per-track request serial and worker result queue, then enriches a matched song in the same background worker through bounded HTTPS song-detail / album-detail requests to obtain `picUrl`. Multi-artist matching now permits the primary artist to identify the result when UI metadata includes a featured/vocal artist that the provider row omits. Cover failures back off from 2s / 6s / 18s to 30s / 60s / 120s instead of polling every 18 seconds forever.

Dominant-color extraction now selects a weighted hue cluster rather than averaging unrelated saturated pixels into a muddy color. It remains presentation-only; per-song DIY color still wins and random-color mutual exclusion remains intact.

## Mirrored exits

H12 exit effects were independent wipe/shrink effects and were not reverse versions of the entrance animation. H19 introduces a recommended `mirror` mode that snapshots the actual per-line entrance and reverses its motion in time:

- soft -> smooth fade-out
- typewriter -> last glyph to first glyph disappearance
- rise -> downward return
- slide -> reverse slide to the left
- bounce -> reverse traversal of the same bounce curve

Explicit fade and instant behavior remain available. Legacy per-char/wipe/shrink config values are migrated to the nearest mirrored effect. New mirrored effects use a 620–1200ms wall-clock duration and do not inherit the old generic upward drift.

No player clock, provider identity, Seek authority, lyric timestamp or precision-selection rule is changed by H19.
