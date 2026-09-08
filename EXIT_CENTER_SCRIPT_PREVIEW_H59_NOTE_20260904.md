# H59 Exit Continuity + Center Corridor + Script Preview

## Field evidence

The H58 field session supplied on 2026-09-04 does not show the capacity or render-pressure emergency valves hard-dropping normal lyric rows. Explicit blank-span releases entered `fading=1` with `emergency_dropped=0`. The same session does contain GUI stalls, so an absolute wall-clock exit can legitimately advance substantially before its first painted frame and look like an instant disappearance even though the row entered the fading lane.

H59 therefore does not weaken player/transport ownership or remove the existing bounded emergency valves. It adds a presentation-only first-visible-frame continuity guard and a diagnostic if a non-instant exit still dies before any exit frame is drawn.

## Exit continuity

All non-`instant` exits cap pre-first-draw wall-clock catch-up to 120 ms. Once one real exit frame is painted, the mature wall-clock lifetime resumes unchanged. The new H59 `hop_drop` exit has the same protection for its own timer.

`轻跃下坠淡出 / hop_drop` rises about 24 px, crosses back down and falls about 48 px while easing alpha to zero. Drawing delegates to the existing H57/H58 fade renderer with only a temporary Y translation, so random fixed depth, composite defocus, outline and Glow remain one immutable birth material.

## Center corridor

H53 remains the collision-safe placement authority. H59 replaces the independent random center coin flip with a deterministic short-window credit quota: 0% never admits center, 100% is unrestricted, and 15% is approximately one admitted row per 6–7 rows without random clusters.

For rows that must avoid center, H59 checks an expanded visual corridor rather than only the final resting footprint. The corridor includes entrance motion, shake allowance, H57 optical/depth margin, perspective mapping and horizontal-wrap copies. If it still overlaps the H53 center box, the anchor is pushed toward the lowest-cost left/right/top/bottom safe band while retaining obstacle/off-screen scoring.

## Script-specific font previews

The Japanese independent-font selector previews Japanese only, Korean previews Korean only, and Western previews Latin/Western only. The general/global font selector keeps the H54 multi-script preview. Coverage status still uses the H51 font glyph check.

## Scope

H59 is presentation-only. It does not modify `MediaSessionSync`, provider requests, lyric transactions, seek authority, player liveness or clock selection.
