# H65 — Continuous Blur Lifecycle

The H64 field session at 18:01 exposed a continuity problem that H64's capacity-aware residency could not solve by itself. H64 capped the returned active-history blur progress at 0.88, but the underlying H62 hold clock continued aging. When `full_text` became blank during a provider-idle/instrumental gap, H64 immediately restored the raw H62 age clock; an old row could therefore jump from a still-visible parked optical state directly to `1.0` and be removed. The same H64 formula also multiplied total row age by the *current* stack-fill speed, so changing the number of live rows could make blur jump forward or move backward.

H65 is a presentation-only closure over H62-H64. While capacity-managed history is active it integrates fill-dependent speed over elapsed time, so fill changes affect only future slope and progress never reverses. When the capacity policy disengages (`full_text` blank or capacity becomes one), H65 rebases H62's hold timestamp to the exact currently visible progress before returning control to H62. Hidden parked age is never paid back in one frame. H63/H62 continue to own explicit release timing and resource retirement.

H65 also changes only the optical mix curve used by H62's already-precomputed Atlas materials. Maximum defocus is reached at progress 0.82, opacity remains fully visible until 0.90, and the final 0.90→1.00 tail fades while maximum blur is held. A quintic smootherstep and a small cross-fade midpoint compensation reduce stage-transition brightness pumping without adding any blur/filter work to `paintEvent` or increasing the number of cached blur Atlases.

Protected player transport, seek, lyric-provider, KuGou golden, QQ software-2 and NetEase authority code is unchanged.
