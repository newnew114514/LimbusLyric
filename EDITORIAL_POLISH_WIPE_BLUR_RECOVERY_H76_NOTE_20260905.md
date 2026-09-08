H76 EDITORIAL POLISH + WIPE REFINEMENT + BLUR RECOVERY (2026-09-05)

Purpose
- Follow up real UI review of H75 without changing player/provider/seek authority.
- Remove product-facing controls that have weak user value, improve discoverability and visual hierarchy, refine the directional wipe flavor, and make progressive blur fail soft instead of disappearing on one update failure.

UI / information architecture
- The legacy renderer `mode_combo` remains persisted for compatibility but its H73 “退场质感” row is hidden from the product UI. H76 does not change the stored `chinese/english` values.
- `字幕显示屏幕` is visible only when `QApplication.screens()` reports more than one display. Screen add/remove events refresh visibility and H51 remains the actual screen-routing owner.
- The title-bar custom-background shortcut becomes a compact palette + `背景` pill. It still opens the H73 background popup; the text removes the icon-guessing problem while retaining a small utility footprint.
- Settings cards become quieter open editorial sections: transparent surfaces, fine separators, lower border density, softer navigation selection, and a stronger Preview Stage hierarchy. No SVG/icon font/runtime dependency is added.

Directional wipe refinement
- Per-character exit is intentionally unchanged and still delegates to H71.
- `wipe_ltr` / `wipe_rtl` no longer use H71’s two distant ghost copies at non-zero flavor.
- H76 uses one low-opacity veil (max 8.5%), 3–9 px opposite-frontier offset, at most 6 px main directional pull, tiny horizontal stretch, no rotation and no second ghost.
- flavor=0 delegates the exact H71/H70 path. H69 edge-wrap topology remains authoritative; flavor/shake cannot choose wrap period.
- H72’s existing wipe dirty envelope is larger than the H76 motion envelope, so no lifecycle/dirty-region expansion is required.

Progressive blur recovery
- H72’s generic exception->retire and 15 s terminal watchdog remain unchanged for non-blur exits.
- Blur-decay uses H76’s own update wrapper. Normal history/deadline planning still delegates to H72/H68.
- Release progress gets a visible minimum tail (normally >=760 ms, pressure floor 560 ms, max 1800 ms) so a row released near H68’s high optical floor cannot look like an instant cut.
- A transient progress/update exception holds the last monotonic optical floor, keeps the row alive, requeues existing H62 material work and requests repaint instead of deleting the row.
- If no release frame is drawn after 520 ms, H76 requests a full repaint/material retry rather than retiring the row.
- The only blur emergency retirement is an absolute 30 s release-age guard and requires at least one confirmed release draw. It is not a normal timing path.
- H69 monotonic optical continuity, H62/H68 material/planner ownership, H72 dirty cleanup and all non-blur exit behavior remain in place.

Boundaries
- No MediaSessionSync, provider, lyric acquisition, seek, clock or transport changes.
- No new worker thread, QImage filtering, paint-time raster operation, SVG or icon-font dependency.
- Per-character H71 behavior is deliberately untouched.

Field-log correction: tail history must enter release
- The H75 field log did not actually show an H72 "forced recycle". It showed H68 at ~0.939 / H69 optical floor ~0.942 followed by `H62渐进失焦历史自然退休 ... reason=age-blur-invisible` while `release=0`.
- H76 therefore treats a no-future-capacity (orphan/tail) blur row differently: once its optical progress reaches 0.92, it is held below the invisible retirement threshold and scheduled history-to-release on the GUI queue.
- Promotion removes that exact row from `history_lines`, calls the existing `begin_fade()` chain (so H72/H69 release-floor rules stay authoritative), appends the row to `fading_lines`, and then lets the H76 visible release tail finish it.
- This closes the case where a tail history row became effectively invisible and was retired before any release frame existed.

Motion grammar / premium feel
- H76 deliberately does not add decorative looping animation. Motion is reserved for state changes, matching the Fluent/PyQt-Fluent pattern of animated stacked pages and flyouts rather than per-control spectacle.
- Page changes use one 165 ms opacity settle (0.84 -> 1.0, OutCubic). The project already had an unused `_animate_current_tab()` concept; H76 connects and standardizes it instead of importing a new animation framework.
- The background utility popup uses a 180 ms fade + 6 px rise. This is a flyout affordance, not a general window animation.
- Buttons/sliders remain immediate and lightweight; Preview Stage owns the expressive motion. The goal is editor/instrument continuity, not a web-dashboard animation layer.

Historical replay boundary maintenance
- `CHECK_INFORMATION_ARCHITECTURE_SPOTIFY_PARITY_H75_REPLAY.py` now scopes its H75 ownership block to the H76 marker when present instead of scanning every future layer to `__main__`.
- H75 runtime/source behavior is unchanged; its existing ban on fading/history lifecycle ownership remains intact inside the H75 block. The change only prevents H76's one reviewed orphan history-to-release promotion from being misattributed to H75.
