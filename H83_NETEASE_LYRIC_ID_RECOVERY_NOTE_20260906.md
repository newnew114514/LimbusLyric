# H83 CODEX SAFE SALVAGE — 2026-09-06

H83 ports only the narrow NetEase lyric-identity closure from the earlier Codex H74 experimental branch onto the current H82 mainline. It does not import that branch wholesale.

- When NetEase is both the selected player and lyric provider, a live native `track_id` may constrain lyric search/version selection only. It never grants clock, seek or playback-status authority.
- NetEase automatic lyric cache keys include the normalized native track ID when one is available, so same-title/same-duration releases with different IDs do not share a cache entry. QQ/KuGou cache shape is unchanged.
- Provider results are checked against both the requested ID and the still-current native player ID before commit; stale late results are rejected.
- If an already-loaded same-title song is bound to a different NetEase ID, a stable 0.6s observation triggers the existing H38 version-reconcile path with the exact ID. Retries are bounded to three, spaced by at least 30s, and in-flight work is not duplicated.
- H45/H46 native clock identity rejection remains authoritative for transport. H49/H50 auto-result ownership and H81/H82 protections remain outer layers.

The donor Codex branch was based on H73 and carried a conflicting product version label `H74`; this port intentionally renames the behavior to H83 to avoid colliding with the current mainline H74 Preview Stage.

Canonical replay: `installer/CHECK_NETEASE_LYRIC_ID_RECOVERY_H83_REPLAY.py`.

## Additional low-risk salvage

- `limbus_netease_native.py` keeps ownership of a cancelling startup task until cleanup really finishes, prevents restart overtaking cleanup, and converts constructor failure into the existing backoff/error state.
- Late H61/H69 row material is accepted only when both lyric text and the held row's actual style signature match, preventing same-text old-style Atlas adoption.
- The old Codex single-slot `MediaSessionSync._poll_loop` redesign and aggressive row-worker queue cancellation were reviewed but intentionally not ported in H83 because they touch shared all-player timing/render scheduling and carry higher field-regression risk.
