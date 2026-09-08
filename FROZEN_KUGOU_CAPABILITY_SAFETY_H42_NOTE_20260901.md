# H42 Frozen KuGou Capability Safety — 2026-09-01

Field evidence from a packaged Windows build `10.0.26200` showed that H37–H41's KuGou safeguards were incorrectly gated by `build < 22000`. The user was running H41, but a valid 163.163s rail seek was later overwritten by a transient proven HostV2 Slider value of 0ms (`host-uia-same-track-restart`). The same machine also reproduced startup COM fatal exceptions and repeated tasklist/subprocess PID timeouts.

H42 keeps historical H37–H41 implementations and their replay contracts intact, but generalizes their runtime safety predicate to packaged Windows KuGou. HostV2 Range remains enabled on capable Win11 builds; its proven duration can become H38 player-owned duration, while a near-zero same-track position is quarantined unless independent recent user/physical near-zero proof exists. False Host zero also cannot advance the KuGou transport generation.

H39's process cyclic-GC protection is extended at the final runtime layer to all packaged Windows processes (environment opt-out: `LIMBUSLYRIC_WINDOWS_FROZEN_PROCESS_GC_GUARD=0`) before QApplication/startup animation. QQ/KuGou PID queries in frozen builds use PSAPI rather than spawning `tasklist`, including the UI reader worker lanes; negative liveness probes retain an 8s backoff with PSAPI positive rescue.

H41's QQ UNKNOWN-motion, NetEase refetch closure, cross-provider lyric completeness gate (`fake town baby` 263s/6-event regression), and other provider behavior remain installed unchanged.
