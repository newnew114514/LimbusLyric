# H95F9 · Translation Alignment + Exit Continuity

H95F9 is a presentation-only correction layer over H95F8.

- Bilingual translation alignment is now monotonic and provider-offset aware. The old +/-900 ms nearest-row proof remains a fallback, but coherent cross-provider offsets and sparse-line drift can be rescued without inventing text.
- Missing provider translation is never machine-generated or duplicated. The UI reports aligned/main coverage and, when applicable, how many timed rows the translation source actually supplied.
- Blur-decay residence material progress is no longer reused as the true release visibility/effect progress. A row may already be optically defocused while resident, but its actual release envelope starts at 0 and receives a visible tail.
- `first-frame-guard` remains a one-frame safety contract; it is not a direct-drop lock. `direct_drop=0` semantics are unchanged.
- No player clock, seek, source identity, provider search order, or lyric timestamp authority is changed.
