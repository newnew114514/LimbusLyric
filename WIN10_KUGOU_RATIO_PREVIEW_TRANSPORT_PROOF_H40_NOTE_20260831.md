# H40 Win10 KuGou ratio-preview + transport-proof closure

H39 field evidence showed three remaining KuGou Win10 holes.

1. An unowned rail gesture was formally blocked but H39 still stamped the legacy gesture timestamp. The normal polling loop then promoted the pre-seek estimator through `_kugou_sync_rail_gesture_anchor()`, recreating an absolute `user-rail-gesture` clock at the old position. H40 no longer stamps that field while duration is unowned. Instead it uses the physical click ratio to publish an immediate, presentation-only seek preview on the current lyric timeline. The media clock remains unchanged until player-owned duration evidence arrives.

2. H38's scale-free physical rail duration probe could starve on low-FPS Win10 VMs because one real rail was often split into several independent two-hit geometry tracks. H40 can aggregate at least three coherent two-hit rail fragments, infer total duration from motion rate, and require a tight consensus before authorizing that duration. This keeps lyric/KRC duration non-authoritative while making player-duration acquisition practical on sparse VM frames.

3. A same-identity GSMTC media edge could still reset KuGou to zero after H38's short post-seek veto expired. H40 treats a same-title transport edge as evidence-only on Win10 until fresh physical rail motion independently proves the playhead is near the beginning. A held edge can still be released for a legitimate same-title replay when that proof appears.

H40 also blocks a stale failed old-song transaction from restoring cached lyrics for a short window after a fresh KuGou identity promotion. Win11 clock/transport policy is unchanged.
