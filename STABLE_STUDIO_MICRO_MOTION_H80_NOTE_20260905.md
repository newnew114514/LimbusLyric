# H80 · Stable Studio Stage + Landmark Micro Motion

## Why H80 exists

H79 removed the dense QWidget opacity fade and replaced it with a light snapshot rise. Field review still found the switch abrupt. The reason is structural: `QTabWidget.currentChanged` fires after the new page is already committed, so H79 was animating a new-page snapshot over an already-visible new page. Higher nominal FPS cannot remove that discontinuity.

H80 therefore stops animating the whole page.

## Product direction

The editing object should remain spatially stable while inspector content changes. The existing H74 subtitle-style and exit-motion previews are real presentation widgets with mature bindings, so H80 re-homes those exact cards into one fixed `Studio Stage` between the workspace header and the scrolling tab content.

- `字幕`: fixed appearance preview stage + scrolling subtitle inspector.
- `动效`: the same fixed stage location switches to the exit preview + scrolling motion inspector.
- Other destinations hide the Studio Stage.
- No duplicate preview renderer, config owner, provider call, or network work is introduced.

## Motion grammar

H80 intentionally retires H79 whole-page snapshot motion.

Only semantic landmarks animate after a destination switch:

- workspace title: 145 ms, 5 px upward settle + opacity;
- first visible section title: 125 ms, 4 px upward settle + opacity;
- navigation indicator: the existing H78 continuous indicator remains;
- Studio Stage mode switch: 120 ms opacity on the small stage card only.

Parameter rows, sliders, combo boxes, scrolling and full pages do not stagger, fly, scale or receive a persistent animation timer.

## Runtime boundaries

H80 is presentation-only. It does not own or modify:

- player/provider selection or clocks;
- seek authority;
- lyric fetching;
- `FadingLine`, blur lifecycle, history/fading residency;
- H76 blur recovery;
- configuration schema or persistence owners;
- background/network threads.

The H74 preview widgets are re-parented, not cloned. H79 live lyric and ambient Hero remain intact.
