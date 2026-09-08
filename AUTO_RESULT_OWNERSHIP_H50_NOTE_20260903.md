# H50 Auto Result Ownership

A rapid A→B→C skip can leave B's provider worker finishing after C has already started.
With `SOURCE_GUARD_ENABLED=1`, those workers intentionally overlap. The historical
`_on_auto_lyric_result()` cleared `_auto_fetch_in_progress` for every final callback before
checking generation/key ownership, so an obsolete B callback could falsely announce that C
was no longer fetching. That weakened manual-fetch coalescing and H46's start-during-transition
arming guard.

H50 is an outer wrapper only. It does not edit the protected historical result handler. For a
final result proven obsolete by generation/key/source/mode, it snapshots the newer transaction,
runs the full historical H38/H41/H49 stack, then restores `_auto_fetch_in_progress=True` only if
the same newer generation and target still own the transaction afterward. Current results,
H49 current-result rejection cleanup, stop/player-change invalidation, and source/mode requeues
remain unchanged.
