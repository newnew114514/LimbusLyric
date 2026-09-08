# H20 Classic Exit + Palette + KuGou Presentation Closure

- Restores the six established H12/H18 exit choices and their exact pre-H19 render paths.
- Adds one optional restrained `soft_drift` exit; H19 reverse/mirror settings migrate back to classics.
- Cover-follow builds a representative palette instead of averaging the image: near-black/white/gray are filtered, tiny chromatic artifacts cannot own a mostly monochrome cover, and colorful covers produce a light readable tint plus a coherent same-hue glow unless per-song DIY explicitly owns text/glow.
- Reuses fresh, already-proven KuGou Host-V2 Range duration as version evidence so H14 does not discard a valid KRC merely because the legacy playlist MSAA probe exceeds 1.25s.
- During KuGou precise long gaps, completed readable history is retained up to the configured visible count while only the current completed row enters the fade lane.
- Same-track manual fast results no longer restart an equal-or-better lyric renderer; repeated clicks while the precise upgrade is pending are coalesced. This prevents visual_count/history from being reset to zero and avoids needless atlas rebuilds.
- Adds an early one-click packaging metadata/structure preflight before dependency installation; canonical gates still run later and remain authoritative.
