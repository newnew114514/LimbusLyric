# H23 Win10 compatibility / reproducible build closure

Scope is deliberately narrow. H23 does not change lyric timing, seek authority, provider selection, QQ/NetEase clocks, or animation semantics.

## Field reason

A Windows 10 build 19045 frozen H21 field run repeatedly found the KuGou window but failed to expose a HostV2 Range control. Individual compatibility probes then took tens of seconds and one process later disappeared without the normal shutdown footer. Public pywinauto issues #1063 and #1222 document Windows 10 UIA/COM calls blocking for about 60 seconds. pywinauto issue #1083 also documents a Windows access violation involving pywinauto/comtypes initialization/shutdown. These do not prove the exact field crash, but they make repeated in-process UIA probing an unjustified risk on that compatibility profile.

## H23 runtime change

`PlayerUiPositionReader.poll()` now decides the Win10-frozen-KuGou safety profile before `_ensure_desktop()`. On Windows builds below 22000 when running a frozen build, KuGou skips creation of `pywinauto.Desktop(backend='uia')` unless explicitly opted in with `LIMBUSLYRIC_KUGOU_HOST_V2_UIA_WIN10=1` (or H23 safety is disabled for diagnostics).

The existing H22 HostV2 Range, hidden Range, point-probe and accessibility-wake guards remain installed as defense-in-depth. H23 additionally suppresses KuGou's in-process comtypes/MSAA playback-clock tree and playlist-duration tree on the exact Windows 10 frozen safety profile. This matters because the failing field log reached the `seeded-msaa-first` fallback lane immediately before the abnormal end, and public pywinauto/comtypes reports include Windows access-violation failures. Win32 title/window discovery, GSMTC evidence, KRC, numeric/Win32 clocks and gesture-local fallback are retained.

H23 intentionally does not force a global COM STA/MTA mode. pywinauto participates in COM apartment initialization and public issue #445 documents changed-mode conflicts; forcing a process-wide apartment policy could regress WinRT/pycaw/other players.

## Reproducible builder

The directly relevant known-good runtime packages from the previous successful build audit are now exact pins:

- PyQt5 5.15.11
- pywin32 311
- pywinauto 0.6.9
- comtypes 1.4.16
- pycaw 20251023
- PyInstaller remains 6.21.0 (already pinned)

The canonical builder now deliberately selects Python 3.12.x, rejects/recreates a reusable build venv made by another Python minor, and runs `VERIFY_BUILD_RUNTIME_PROFILE.py` after dependency installation. This prevents the same source tree from silently producing a different COM/UIA frozen runtime when the build machine's default Python or pip resolution changes.

## Non-goals / remaining risk

- No claim is made that Linux CI reproduces Windows 10 native COM behavior.
- On Win11/non-frozen environments H22's retrospective slow-call fuse cannot interrupt the *first* native UIA call while it is blocked. Full hard deadlines would require process isolation, which is intentionally deferred unless field evidence shows it is needed.
- Native MSAA remains enabled outside the exact Win10 frozen KuGou safety profile. On that profile it is intentionally disabled in-process; if precise version discrimination becomes insufficient, the safe future design is an isolated helper process rather than restoring unbounded COM traversal inside the main process.

## Final release audit

- Canonical suite count after H23 gate addition: 81.
- Behavior/replay gates 1-79 were rerun on the H23 source before updating the final source lock and manifest.
- Final packaging structure/source-lock checks are rerun after metadata regeneration and again from an extracted release ZIP.
