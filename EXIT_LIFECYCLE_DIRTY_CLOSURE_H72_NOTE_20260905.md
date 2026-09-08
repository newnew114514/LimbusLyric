# H72 Exit Lifecycle + Dirty-Region Closure — 2026-09-05

## Field symptom

The H71 field session for `赤と青` exposed two lifecycle failures that are independent of the artistic flavor amplitudes:

1. A row can retire from `fading_lines` while a flavor-transformed glyph remains visible on the translucent backing surface. H70/H71 may translate/scale/ghost pixels outside the mature row/fragment dirty box, but the sparse repaint contract still only knew the old geometry. H71 made that mismatch large enough to become visible as a lone stuck character.
2. H68 can park active blur history at `0.939` after its synthetic/capacity horizon reaches zero. The horizon and active progress used monotonic wall time, so a playback pause could consume deadline/progress while the media clock was frozen. Tail rows may also have no future capacity eviction at all, leaving a faint history row with no event that starts the release phase.

The field log contains no Python traceback. It also shows history/fading bookkeeping returning to zero in one segment while the user still observed a residual glyph, which is consistent with stale pixels outside the registered sparse-dirty envelope rather than an object necessarily remaining in `fading_lines`.

## H72 closure

### 1. Effect-native dirty envelopes

`LyricWindow._held_visual_region()` is wrapped after H71. The region now reserves the maximum optional H70/H71 motion for the selected effect:

- whole-row fade: upward travel;
- per-character: scatter/rotation envelope;
- directional wipe: first and second ghost trail envelope;
- shrink: pretension scale expansion;
- soft drift: extra gravity travel;
- hop/drop: extra vertical trajectory and rotation safety;
- progressive blur: depth-spread scale expansion.

The last expanded region is retained on the row. When the row retires, that region is copied to `_pending_explicit_region` before render resources can clear fragment bounds. If no reliable region exists for a flavored row, the next repaint is forced full as a fail-safe.

Direct pressure/burst retirement is covered too: `_discard_fading_item()` is wrapped so it invalidates the expanded envelope before releasing resources. This closes paths which bypass `FadingLine.update()`.

### 2. Playback-clock H68 active deadline

H68 remains the owner of capacity-aware blur planning, velocity smoothing, and release continuity. H72 changes only its clock source while a blur row is active in history:

- remaining exact capacity horizon is derived from future lyric start minus the sampled player position;
- active integration elapsed is derived from positive player-position delta, not monotonic wall-clock delta;
- pauses therefore consume neither future horizon nor blur progress;
- one anomalous/seek sample cannot inject more than 1200 ms of active integration; existing seek/epoch reset paths remain authoritative.

### 3. Tail history with no capacity eviction

If `origin + capacity` does not exist in the loaded timeline, there is no legitimate future capacity event that can release the row. H72 lets that row finish H62's natural hold progression using playback position. It can therefore reach `progress=1` and be removed by the existing H62 natural-retirement path instead of parking forever at H68's active `0.939` ceiling.

This exception applies only when an exact future capacity eviction is impossible. Normal capacity-managed rows retain H68's active-limit/release split.

### 4. Blur handoff floor

At `history -> fading` handoff H72 snapshots the maximum already-visible optical/capacity progress. If an older producer initializes release below that floor, the release starts from the visible floor. This is a robustness closure; the field log's adjacent H65/H63 progress messages are not assumed to represent the same row.

### 5. Terminal watchdog

All non-instant fading rows receive a 15 s hard lifetime ceiling. It is deliberately much longer than normal H70/H71 effect durations and is only terminal insurance for an update path that would otherwise never return `False`. It does not redefine normal user speed or deadline adaptation.

## Scope

H72 does not change H71 flavor amplitudes, H70 per-effect speed profiles, lyric/provider selection, player clock authority, seek ownership, subtitle placement, Atlas raster semantics, or one-click packaging commands. It is a presentation/lifecycle closure around sparse invalidation and blur time ownership.
