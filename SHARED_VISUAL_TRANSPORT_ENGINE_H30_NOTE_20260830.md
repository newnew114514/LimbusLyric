# H30 Shared Visual Transport Engine — Cross-Windows Closure

Field evidence from the Win10 VM proved two things at once: H29 could physically lock NetEase progress, but repeated/late VM frames made the lock intermittent; meanwhile Win11/KuGou still used a different visual tracker. H30 removes that semantic fork.

## Unified visual transport core

NetEase and KuGou now route screen-derived transport evidence through one shared temporal state machine on Windows:

1. provider-safe window rectangle/capture adapter;
2. compact temporal motion clusters;
3. rail geometry association;
4. persistent geometry identity across sparse frames;
5. multi-sample playback-pace proof;
6. physical anchor + bounded monotonic lease;
7. seek invalidation/reproof;
8. pause freeze and track-epoch reset.

Win10 and Win11 may still expose different auxiliary APIs. Win10 frozen keeps the H24 accessibility fail-closed boundary; Win11 may continue to use GSMTC/UIA/native evidence. What is now shared is the visual position/rail/seek evidence semantics.

## Sparse VM/DWM behavior

H29 field logs locked NetEase at 5.397s, 134.198s, and 146.172s, but many intermediate captures were duplicate frames. H30 keeps proof histories for up to 60s and a verified visual anchor for a bounded 24s lease. A transport interaction invalidates stale extrapolation and requires a short physical reproof.

## CloudMusic PID ownership

CloudMusic PID resolution is now closed through one exact HWND/PID witness. `LyricFetcher.get_player_pids`, `PlayerUiPositionReader._process_pids`, `AsyncPlayerUiPositionReader._process_pids`, and the final liveness probe all avoid CloudMusic tasklist/full-system enumeration. Missing evidence is UNKNOWN rather than a fabricated process death.

## Compatibility boundary

Historical H1-H29 code remains in place and source-locked. H30 is a final ownership layer. QQ transport behavior is unchanged. KuGou GSMTC/UIA/native paths remain auxiliary and its visual commit still seeds the existing rail-local-master only after the shared physical proof.

No Windows executable is built in this Linux environment; this release ZIP is the source/release package for Windows build/test.
