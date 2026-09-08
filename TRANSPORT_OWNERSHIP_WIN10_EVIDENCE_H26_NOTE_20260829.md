# H26 Transport Ownership + Win10 Evidence Closure — 2026-08-29

## Why H26 exists

Win10 19045 frozen field replay proved that H25's intended `UNKNOWN` contract was not end-to-end. NetEase native, strict GSMTC and H25 visual clock could all be unavailable while the older generic auto-local lane still published a convincing `0ms`. The same audit also found provider/player ownership leaks: selecting a lyric provider could trigger that provider's desktop process/UIA probes even when another player owned playback.

H26 treats these as separate contracts:

1. **Playback transport belongs to the selected player.** Lyric providers may supply network lyric payloads, but cannot read another open player's PID/window/UIA clock as identity or duration evidence.
2. **No evidence means no position on Win10 NetEase safe profile.** Generic auto-local bootstrap is suppressed and any stale provisional-local publication is converted back to `None` before the renderer.
3. **Win11 remains on the accumulated H25 transport path.** H26 NetEase UNKNOWN/visual special handling is gated by the existing Win10 frozen safe-profile predicate; non-safe/Win11 calls delegate to the previous implementation.

## NetEase native lifecycle

`limbus_netease_native.py` now bounds detector startup and shutdown. A detector whose `start()` never returns becomes an explicit `start-timeout:*` state and is bounded-stopped instead of staying forever in an ambiguous `available=1/error=none/title=<empty>` state. A healthy detector still returns the same native track ID, metadata and position.

## Win10 visual clock

H25's motion-first rail bootstrap was replaced by a Win10-only static-rail geometry shortlist followed by time authority proof. Candidate geometry alone owns no time. Authority requires at least three coherent samples, at least 900ms span and real forward boundary motion. A static horizontal line, stale samples across a scheduling gap, or a capture failure cannot become a clock.

Field diagnostics now distinguish `no-window-rect`, `capture-failed`, `no-horizontal-rail`, `proof-pending`, lock and seek-reconfirmation states without enabling Chromium UIA/MSAA.

## Transition latency / occasional lyric lag

The historical metadata detection-latency provisional origin remains the fallback. H26 only replaces it when the already-running selected player exposes a strong, source-affine, same-track position. Weak provisional evidence, wrong-track metadata or another player's session leaves the historical value unchanged. This targets occasional multi-second late starts without inventing a new generic Win11 clock.

## Compatibility boundary

H26 is implemented as a post-H25 layer. Legacy class methods are not edited to obtain the new behavior. The existing legacy source locks, KuGou golden locks and QQ protected adapter lock must continue to pass. The new H26 gate additionally verifies Win10 fail-closed behavior and exact Win11/non-safe delegation.

Canonical release suite: **84 gates**, including `installer/CHECK_TRANSPORT_OWNERSHIP_WIN10_H26_REPLAY.py`.
