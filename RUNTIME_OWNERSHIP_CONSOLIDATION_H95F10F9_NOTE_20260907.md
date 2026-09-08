# H95F10F9 — Runtime ownership consolidation (phase 1)

This release begins structural consolidation without changing transport/provider authority or the user's visual presets.

## Why this layer exists

F8 field evidence showed that the steady renderer can be fast, while isolated cache misses still create very large paint spikes. F8 also repeated current primary/translation cache scans and created a new raster thread for each prewarm token. Separately, the final H95F7 bridge temporarily replaced a process-global translation lookup during every paint.

## Changes

- Adds one per-paint render-input **FramePlan** for current line index, primary/translation text, material style and cache state. It is not a new renderer and does not own timing/effect formulas.
- Treats **one visible missing glyph** as cold. The existing plain-glyph emergency renderer is used briefly until the styled sprite arrives; no glyph rasterization is allowed in the final F9 paint function.
- Replaces F8 thread-per-token prewarm with one long-lived, low-priority, stale-cancellable worker.
- Prewarms the current primary/translation lanes first, then the next primary/translation row from a GUI-idle callback. Typography resolution for the neighbour is therefore outside paint.
- Preserves `displayed_line_index == 0` exactly.
- Removes the final H95F7 process-global translation-lookup mutation. Legacy duplicate translation passes are suppressed with a window-local flag while the mature primary renderer runs.
- Reuses F8's existing one-QPixmap-per-tick cache installer and all mature H51/H57/H62/H70/H95F* visual owners.

## Explicit non-goals

- No `MediaSessionSync` clock/seek/bind changes.
- No `LyricSearchEngine.search` changes.
- No QRC/KRC/YRC/provider arbitration changes.
- No entrance/exit/shake/depth/audio formula changes.
- No UI redesign.

## Architecture audit snapshot

The canonical main source still contains a long historical patch chain. Static audit of the F8 baseline found 35 `ControlPanel.__init__` assignments, 11 `FadingLine.draw` assignments, 4 `LyricWindow.paintEvent` assignments and 3 `LyricSearchEngine.search` assignments. H95F10F9 deliberately does not collapse those historical layers in one release. The next safe consolidation targets are background visual work scheduling and final visual-state snapshots, followed by retiring redundant wrapper layers only after behavior replay coverage exists.
