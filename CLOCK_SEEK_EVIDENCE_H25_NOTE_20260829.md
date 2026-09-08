# H25 Clock / Seek / Evidence Closure — 2026-08-29

H25 is an evidence-driven follow-up to H24 based on the full 2329-line Win10 19045 frozen/VirtualBox field log. It keeps H23/H24 accessibility crash hardening intact and closes the remaining clock/seek/version-evidence regressions without re-enabling Chromium UIA/MSAA tree traversal.

## Confirmed field issues closed

- **NetEase normal playback position was unobservable in H24 safe mode.** The log had valid 221.5s lyrics/YRC but precision handoff reported `position=none | target=-1`, while strict current GSMTC belonged to KuGou and was correctly rejected. H25 adds a Win32/GDI screen-pixel rail observer on the MediaSessionSync worker. It requires three geometry-consistent, wall-clock-coherent samples before becoming position authority. No pywinauto/comtypes/Chromium accessibility tree is used.
- **NetEase seek lost its re-anchor path.** A verified transport click now becomes seek intent only. If a previously proven physical rail exists, the click may seed a short provisional position and then must be visually reconfirmed. Paused seeks stay paused; they never start a synthetic playing clock. Unknown remains unknown instead of being manufactured as hard 0ms.
- **NetEase safe visual capture initially started too low.** Field clicks clustered near the top of the transport band, so the capture strip now begins at 0.775 of client height, covering the progress rail while remaining restricted to the lower transport region.
- **KuGou 81s candidate could self-certify.** A lyric-provider/cache duration can no longer create a verified duration row by itself. Session-verified duration requires an independent player-side duration corroborating the same version.
- **KuGou manual/auto artist enrichment could bypass marquee/shell rejection.** Both enrichment paths now pass the same Host-title credibility filter used by ordinary identity detection.
- **KuGou committed seek could be immediately reset to local zero by ambiguous same-identity transport callbacks.** A narrow 1.5s veto applies only after a committed absolute user rail gesture for the same track/player/identity epochs. Broad mouse-down candidates do not arm it.
- **Manual KuGou payload could be immediately downgraded by a conflicting automatic same-instance candidate.** The manual payload is a session preference, not duration proof; a conflicting auto payload is blocked unless independent player duration supports the incoming version.
- **Diagnostic flood.** Repeated marquee/GSMTC recovery logging is coalesced without changing authority behavior.

## Preserved boundaries

- H23 Win10 frozen KuGou remains no in-process UIA/MSAA accessibility-tree traversal.
- H24 Win10 frozen NetEase remains no Chromium UIA wake, targeted scan, or deep UIA worker by default.
- QQ Software-2 timing/seek authority is unchanged; the three historical outer-method locks changed only for reviewed NetEase safe-clock / KuGou identity-enrichment wiring and are re-locked accordingly.
- Provider lyric timestamps are not rewritten to compensate for clock problems.

## Release validation

Canonical suite: **83 gates**, including `CHECK_CLOCK_SEEK_EVIDENCE_H25_REPLAY.py`. The H25 replay covers provider-duration self-certification rejection, KuGou marquee enrichment, committed-seek zero-reset protection, NetEase no-accessibility visual clock proof, capture-band coverage, safe seek seeding, and fail-unknown behavior.
