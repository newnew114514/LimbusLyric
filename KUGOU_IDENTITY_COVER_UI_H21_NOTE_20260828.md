# H21 KuGou identity + cover UI closure (2026-08-28)

## Real-machine evidence
- H20 host log at 22:04:41 showed Host-V2 title `草东没有派对 - 但 - 酷狗音乐` and a real rail collapse to 0ms. ControlPanel correctly reset from the prior remix to `但|草东没有派对`.
- In the same second a fresh GSMTC title-change notification still carried the previous `少女A (one day After Another Remix)` title and immediately reset identity back to that stale song. The failed transaction then relaunched cached lyrics for `但`, leaving presentation and media identity split; later KRC duration completion logged `track-mismatch`.
- H20 also showed Host-V2 duration could arrive just after H14 started its separate bounded MSAA duration probe. The probe timed out and H14 discarded an otherwise valid KRC even though current Host-V2 and KRC durations agreed.

## H21 changes
- A just-selected, still-current Host-V2 switch gets a 3.0s conflict veto over `kugou-gsmtc-title-change`. Only conflicting GSMTC identity is rejected; matching enrichment is untouched. A stable old Host-V2 title never creates the guard.
- Host-V2 duration hints are cached under both the internal transport key and the fresh Host-V2 window-title song, closing the brief identity-handoff key mismatch.
- H14's named duration worker gives the live Host-V2 path 0.55s to publish before starting legacy MSAA. If legacy proof still times out, a returned KRC is rescued only when a fresh Host-V2 duration for the exact title agrees within max(1200ms, 1.2%). Without this independent proof, original H14 drop behavior remains unchanged.
- The existing `歌词颜色跟随封面` checkbox is moved into the subtitle style row beside random font/random color. The same widget, signal and `h12_cover_follow` config key are retained.

## Non-goals
- No KuGou rail/Seek/transport timing authority changed.
- No provider timestamps or lyric clock math changed.
- No new cover-follow config key or duplicate checkbox.

## Dedicated gate
- `installer/CHECK_KUGOU_IDENTITY_COVER_UI_H21_REPLAY.py`
