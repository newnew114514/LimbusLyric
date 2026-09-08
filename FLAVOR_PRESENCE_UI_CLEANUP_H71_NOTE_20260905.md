# H71 Flavor Presence + Instant UI Cleanup (2026-09-05)

H70 established per-effect remembered speed and one optional effect-native flavor, but field feedback showed that several flavor maxima were too conservative to read as a genuinely different style at normal desktop scale. H71 keeps H70's ownership model and speed/deadline adaptation unchanged, and recalibrates only presentation amplitude.

## Visual presence calibration

`flavor=0` remains an exact delegate to H70/H69/H51. Above zero, H71 uses a bounded presence curve (`x^0.72`) so the middle of the slider becomes useful instead of reserving nearly all visible change for the final few points. The maximums are also raised in effect-native directions:

- per-character disappearance: larger stable per-glyph drift, stronger timing scatter, up to about 7.5° local rotation, and a faint counter-echo;
- directional wipe: a wider feather plus two bounded glyph-shaped afterimages, with the second trail deliberately faint;
- quick shrink: H70's pretension is retained and an additional bounded pre-tension layer makes the high end clearly readable;
- soft drift: additional late gravity displacement strengthens the sense of weight without altering its duration;
- hop/drop: larger arc displacement plus a bounded extra rotation, still one ballistic motion rather than repeated springing;
- progressive blur: additional spatial expansion reinforces the depth-defocus impression without changing H68/H69 blur progress or release timing;
- classic whole-row fade keeps the already-readable H70 rise-distance behavior unchanged.

H71 changes artistic amplitude only. Per-effect `退场速度`, H70 dense-song soft deadlines, H68/H69 blur deadline/monotonic continuity, and direct-drop protections are not retargeted.

## Fragment-material reliability

Per-character and wipe flavors need immutable row fragment material. H70 correctly degraded to the mature whole-row fallback if that material was unavailable, but that also meant the optional flavor could disappear completely for that row. When either flavor is enabled, H71 now requests the existing H61 asynchronous row-atlas worker at history-row birth if no shared fragment atlas is present. Late H69 material adoption remains responsible for attaching completed material; no synchronous raster work is introduced into paintEvent.

## Direct disappear UI

`instant` owns no animation lifecycle. H71 therefore hides both dynamic profile rows (`退场速度` and the effect-specific flavor) instead of showing disabled controls / `无动画`. Selecting another animated exit restores the remembered controls immediately. The profile data is retained for other effects and no config schema reset is required.

## Scope

Presentation only. Player clocks, seek/provider authority, lyric acquisition, capacity residency, H68/H69 blur timing, packaging commands, and one-click build semantics are unchanged.
