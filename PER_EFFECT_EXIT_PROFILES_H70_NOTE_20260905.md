# H70 · Per-Effect Exit Profiles + Optional Flavor Layer

## Why
H69 made progressive blur optically continuous, but the exit-settings model was still asymmetric: the classic whole-row fade owned the legacy fade/rise controls, several other exits inherited only parts of `fade_speed`, hop/drop used a fixed timer, and H68/H69 blur used its own deadline planner. Users therefore could not remember a distinct preferred speed for each exit, and the old global rise control had no meaningful role for most effects.

## User contract
Each public exit effect now remembers two values independently:

- **退场速度** — one consistent user intent: slower ↔ faster. Internally each effect translates that intent into its own mature timing model.
- **专属风味** — one effect-native optional modifier. `0` delegates the existing H69/H59/H51 renderer and preserves the original visual language.

Direct disappear remains parameter-free.

Profiles are snapshotted into a row at birth. Changing a slider affects later rows only; an already-running exit never retargets because the user switched effects or adjusted a control.

## Flavor mapping
- `fade` → **上升距离**: additive total-distance rise on the same fade timeline. No frame-rate-dependent rise velocity.
- `per_char` → **离散度**: stable per-glyph timing jitter plus bounded deterministic local drift; wrap topology still uses H69 stable geometry.
- `wipe_ltr` / `wipe_rtl` → **拖尾**: a wider wipe frontier plus one bounded low-opacity trailing glyph fragment.
- `shrink` → **蓄力**: one short pre-tension overshoot before the existing quick shrink. No repeated bounce.
- `soft_drift` → **重力感**: additional late-phase downward acceleration while retaining the original soft drift.
- `hop_drop` → **弹性**: larger hop/drop arc; only high flavor adds a very small deterministic rotation.
- `blur_decay` → **景深扩散**: a subtle scale expansion during defocus. H68/H69 owns optical progress and material continuity unchanged.

## Timing / adaptive behavior
Classic fade, per-character and directional wipe continue to use their mature duration logic with the profile speed snapshotted into `row.fade_speed`.

Quick shrink and soft drift had historical clamps that made much of the old 1..15 range visually identical. H70 calibrates those effects around their old speed=12 defaults while making the full range useful.

Hop/drop and blur had fixed/native planners, so H70 translates speed through a bounded nonlinear time scale rather than replacing those engines.

At release, non-blur effects receive a soft future-cadence budget derived from the same known lyric timeline used by H68. Only excess duration is compressed. Effect-specific visible minima remain authoritative, and the artistic flavor value is never modified by the adaptive scheduler.

Blur remains on H68/H69's capacity/deadline planner. H70 scales its tail preference but preserves monotonic progress, active→release velocity continuity and direct-drop protection.

## Compatibility
Pre-H70 settings migrate deterministically:
- all effects start with the old global `fade_speed` as their speed preference;
- only classic fade migrates the old `rise_speed` into its new total-rise flavor;
- all newly introduced flavors start at 0;
- new full-style presets store/restore the complete profile map;
- old presets without H70 data are migrated from their legacy fade/rise fields when loaded.

The old fade/rise widgets remain internally for configuration/preset compatibility but are hidden from the UI to avoid competing controls.

## Engineering boundaries
H70 is presentation/configuration only. It does not touch MediaSessionSync, provider authority, lyric acquisition, seek ownership, player control, Win32 accessibility or packaging commands.

Reference ideas were taken from mature animation-system patterns rather than copied implementations: a single normalized timeline with staggered property intervals, parameterized easing/overshoot, and velocity/timing continuity. H70 uses those principles on top of the project's existing Qt renderer.
