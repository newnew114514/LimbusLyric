# H24 Win10 runtime safety closure — 2026-08-29

## Field evidence

Two Win10 19045 virtual-machine replays exposed issues not covered by H22/H23:

1. **NetEase/Chromium accessibility can stall the player itself.** The session log showed `cloudmusic` alive, followed by `网易云定点UIA请求已下发` / `网易云页面交互触发UIA快扫`, while no corresponding accessibility-wake completion/failure appeared. The lyric APIs continued to return normal LRC/YRC, so provider/network fetch was not the failing lane.
2. **KuGou top-level title can be a rotating marquee.** The same `kugou_ui` HWND emitted cyclic title slices such as `酷狗音乐 鏡音リン、椎名もた - 少女A -` -> `狗音乐 ... - 酷`. Some slices accidentally parsed as valid song/artist identities and repeatedly reset the same song. H21 could then protect that false Host identity and veto the correct GSMTC identity.
3. The same session first proved a ~221s KuGou KRC, then a stale ~81s same-title cache was later eligible after identity churn.
4. `auto_lyric_cache_v1.json` could be empty/corrupt and logged a JSON traceback on every startup.

## H24 changes

- **NetEase Win10 frozen fail-closed accessibility profile** (default on, opt-out available):
  - `cloudmusic.exe` on frozen Win10 (< build 22000) keeps the async UIA worker suspended.
  - skips WM_GETOBJECT/pywinauto accessibility wake;
  - skips urgent/targeted UIA scans and lyric-text UIA probes;
  - prevents Bridge/native fallback code from re-enabling UIA on that profile;
  - keeps native/GSMTC/network lyric lanes intact;
  - QQ UIA behavior is unchanged.
- **KuGou marquee identity fuse**:
  - detects cyclic same-HWND title rotation;
  - rotating Host title remains usable for window discovery, not track identity;
  - split `酷狗音乐` shell fragments across parsed song/artist are rejected;
  - during the marquee fuse, H21 cannot use Host identity to veto process-affine GSMTC.
- **KuGou session verified-duration guard**:
  - first accepted strong same-song duration is remembered for the session;
  - later KuGou jobs with no independent player duration inherit that witness;
  - an incompatible same-title cached duration cannot downgrade the verified session version;
  - a genuinely new version can still replace it when independent player duration supports the new duration.
- **Persistent cache self-heal**:
  - malformed/empty auto lyric cache is renamed to `.corrupt-<timestamp>` when possible;
  - a valid empty JSON cache is atomically recreated before legacy loading continues.

## Deliberately unchanged

- QQ source-locked UIA/clock/seek paths.
- KuGou golden source-locked transport/rail/seek methods.
- H18 liveness authority and player-dead retirement semantics.
- H14 auto-precision budget.
- Provider network timing and user playback controls.

## Replay gate

`installer/CHECK_WIN10_RUNTIME_SAFETY_H24_REPLAY.py` covers the exact field marquee rotation, split-shell rejection, Win10 NetEase no-UIA predicate, 221000ms -> 81000ms duration downgrade rejection, and cache self-heal wiring.
