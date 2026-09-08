# H36 KuGou Visual Authority + NetEase Bootstrap Closure

Host evidence from `LimbusLyric_20260831-144441_pid27440.log` identified two separate authority failures.

## KuGou

An already absolute Host-V2 rail clock was near 87.1s when the shared visual detector repeatedly selected a different moving edge near 49.0s. H34 treated repeated frames from that same visual candidate as second proof and rewrote the local master backwards by about 38s.

H36 makes the authority hierarchy explicit: after the current track/player/identity epoch owns an **absolute** KuGou local master, `visual-rail-auto` may perform only bounded corrections. A visual-only candidate farther than `max(8s, 4% of duration)` is rejected. Initial/unanchored visual acquisition remains allowed, and Host-V2 Range or an explicit user rail gesture continue to be independent absolute authorities.

## NetEase

The host source run reported `No module named 'limbus_netease_native'` and entered UIA/GSMTC fallback. H36 retries the shipped sibling `limbus_netease_native.py` by exact file path before declaring the adapter unavailable. The adapter's optional `cloudmusic_detector` dependency policy is unchanged; the Windows installer still pins and bundles `netease-cloudmusic-detector==2.0.6`.

When fallback is genuinely required, a duration-matched `uia-doc-point` first sample remains provisional and receives no Seek authority, but it is now allowed to drive presentation immediately instead of being hidden behind the auto-track local clock. With unknown GSMTC status, a second sparse Document sample must demonstrate natural forward pace before H36 extrapolates between scans. Large seek-like jumps remain outside this continuity lane and continue through the existing seek/user-interaction arbitration.

## QQ

No QQ authority policy is changed in H36. The host log showed the existing QQ far-sample quarantine correctly rejecting a one-frame 241s observation while the trusted clock was near 140s.
