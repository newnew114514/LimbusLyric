# H32 — KuGou Seek Observer + QQ Capacity + Native Position Sanity

## Field evidence

The H31 Win10 field session showed NetEase native detector 2.0.6 operating successfully, including explicit native seek callbacks. Three remaining defects were independent of that success:

1. **KuGou seek observation could be starved by a silent hook.** `WH_MOUSE_LL` reported ready, HostV2 continuously resolved the real `kugou_ui` host, but no gesture-consumption diagnostics or `H28酷狗真实Seek观察已接管` appeared. The shared visual tracker also remained `geometry=0`. The source returned immediately whenever the hook-ready flag was true, permanently disabling its `GetAsyncKeyState` fallback.
2. **QQ used legacy residency despite carrying multiple rows.** Field diagnostics reached `live_count=3/history_count=2`, but every QQ row reported `residency=legacy`; NetEase reported `residency=capacity`. Provider-idle and seek boundaries therefore retired QQ history more aggressively than the configured multi-subtitle capacity implied.
3. **A NetEase detector position could contain a wall-clock-like value.** One delta-fallback logged `observed=1788096637457ms`, which was then treated as a seek and moved presentation near the end of the song. The adapter multiplied every detector position by 1000 without validating units/range against duration.

A smaller transition race was also visible: immediately after a native detector track-serial edge, H31 could publish one old-track continuity frame before ControlPanel finished binding the new identity.

## H32 behavior

- KuGou publishes geometry-only rail bounds from an already cached HostV2/DWM rectangle. It performs no synchronous window discovery in the GUI/snapshot hot path.
- The original low-level hook is retained. H32 additionally observes `GetAsyncKeyState(VK_LBUTTON)` and cursor position on the cheap snapshot cadence. The poller never calls `SendInput`, `mouse_event`, or `SetCursorPos`; it only observes the user's real click/drag and reuses the existing KuGou seek commit/reanchor path. A hook commit in the same frame suppresses the poll commit.
- QQ opts into the existing capacity-residency semantic switch. Provider-idle release preserves held QQ history up to `max_visible_subtitles - 1`; transport/GSMTC/UIA authority is untouched.
- `limbus_netease_native.py` now normalizes detector position using track duration. Seconds are preferred when valid, already-millisecond values are accepted when the seconds interpretation is impossible, and values outside a bounded duration corridor are rejected as `invalid-position-range`.
- A recent native track-serial transition revokes `ncm-trusted-continuity-local` immediately, before the later ControlPanel track bind.

## Regression contract

`CHECK_KUGOU_SEEK_QQ_CAPACITY_NATIVE_SANITY_H32_REPLAY.py` verifies native seconds/ms/epoch normalization, cached KuGou HostV2 rail publication, no mouse injection tokens, QQ capacity/provider-idle history retention, and native-track-edge continuity revocation. Historical H14/H16/H18/H22-H31, legacy, KuGou golden, KuGou clock/seek/rail, QQ clock/handoff/loop, and GUI hot-path gates remain required.
