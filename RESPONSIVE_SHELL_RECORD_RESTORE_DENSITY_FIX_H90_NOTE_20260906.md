# H90 · Responsive Shell / Record Restore / Density Fix

H90 is a presentation-only response to Windows field feedback after H89.

- Retires the H88/H89 section-chip rail completely. Long settings remain normal scroll content.
- Restores the Listening Room / record at compact widths; the old `<800 px => hide ambient` rule is overridden after the historical Studio layout runs.
- Reduces normal minimum window geometry to 520×360 and lets the scroll-based settings shell ignore oversized child size hints vertically.
- Re-applies compact shell constraints after H12 UI scaling, so 125%/150% text scale does not force a near-full-screen normal window.
- Retires the extra H86/H89 title-bar native resize transaction. The top edge now relies on ControlPanel's existing `WM_NCHITTEST` four-edge/corner implementation; a client top-strip press is ignored instead of becoming a window move.
- Keeps delayed geometry rescue only for genuinely off-screen/oversized normal windows and never changes geometry while the left mouse button still owns a resize gesture.

No MediaSessionSync, seek, player/provider identity, lyric search, lyric timeline, FadingLine, OBS, or desktop overlay authority is changed.
