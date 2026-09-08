# H78 Studio Navigation + Typographic Layout

H78 is a presentation-only continuation of H77/H76. It responds to field feedback that the control panel still felt like a polished settings utility and that some visual controls were filed under the wrong product surface.

## Product changes

- The top-right shell utility is permanently named **界面**. H76's background-toggle callback is rebound so selecting/clearing a background can no longer rename the utility back to **背景**.
- The Interface popup remains the single shell-level home for **界面缩放** and **自定义背景**. The hidden H12/H75 owners continue to own persistence.
- The mature H51 card is physically re-homed from Settings to Appearance and renamed **排版与布局**. It keeps the original center-frequency slider, per-line size range, Japanese/Korean/Western font overrides, and the H76 conditional multi-monitor target row. No duplicate controls or new config keys are created.
- Appearance page metadata now explicitly includes typography/layout; Settings no longer advertises interface/background/visual controls.

## Motion grammar

H76's 165 ms / 0.84 opacity settle was structurally correct but too subtle in field use. H78 replaces the presentation method with:

- page opacity reveal: **0.52 -> 1.0 / 245 ms / OutCubic**;
- workspace-header settle: **0.70 -> 1.0 / 220 ms / OutCubic**;
- moving top-navigation selection surface: **225 ms / OutCubic**.

The navigation indicator is a low-alpha moving surface behind the existing buttons. There is no zoom, bounce, spring, scroll animation or lyric-render-loop animation.

## Editorial shell

- Top navigation becomes a quiet studio rail with one moving selection surface.
- Workspace kicker becomes `01 / PLAYBACK`, `02 / APPEARANCE`, etc.
- A 3 px muted-rose workspace mark provides a consistent editorial anchor.
- Existing H77 Hero / Inspector semantics remain authoritative; H78 does not introduce another visual theme system.

## Runtime boundaries

H78 does not modify MediaSessionSync, lyric providers, seek, FadingLine, blur/exit lifecycle, placement, dirty regions, threads, config schema, or packaging topology. H76 remains authoritative for wipe/blur recovery and conditional multi-monitor visibility.
