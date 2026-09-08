# H67 Capacity-Cadence Blur Governor — 2026-09-04

## Field finding
H66 removed the 0.88 shelf and direct render-pressure drops, but its active residency speed was still:

`speed = min_speed + (1-min_speed) * (live_count / capacity)`

That makes a saturated 3-row stack (`3/3`) and saturated 6-row stack (`6/6`) identical. The H66 field log also showed age-driven retirement while a six-row target was still under-filled, so the slider behaved more like a loose ceiling than a stable visual residency target.

## H67 behavior
H67 keeps the H66 optical curve and pressure-safe release, but replaces the active capacity slope with a predictive controller:

1. Observe sequential completed-row wall cadence with a clipped EMA. Seek/prefix snapshots do not update the cadence sample.
2. For each history row, compute how many future normal row births remain before capacity overflow releases that exact row.
3. Drive only future blur slope so the row approaches `0.875` near predicted overflow.
4. If it gets ahead of target, continue asymptotically toward `0.938` (just before H66 opacity begins at `0.94`) instead of hard parking or self-deleting.
5. Capacity overflow remains the active-flow retirement authority. Provider idle still rebases to the raw H62 clock and may naturally retire old rows.
6. Capacity=1 gets a cadence-scaled release tail so a clear previous line does not spend the old multi-second full release when the user explicitly requested one visible subtitle.

## Safety boundary
No media clock, seek authority, provider identity, lyric acquisition, placement, Atlas build path, packaging command, or non-blur exit policy is changed. H67 adds only one lightweight cadence observer on completed history creation and replaces the blur-decay progress governor.
