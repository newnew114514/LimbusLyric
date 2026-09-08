# H22 KuGou Win10 Crash Hardening — 2026-08-28

## Field evidence

Two H21 logs from the same Windows 10 19045 frozen environment were reviewed.

- Session A ended normally with the full Stop -> Qt quit -> log-session footer chain.
- Session B ended abruptly without an exit request, traceback, or log-session footer.
- KuGou's top-level `kugou_ui` window was found, but the HostV2 UIA progress Range never appeared.
- The same in-process pywinauto Range walk returned `progress control not exposed` at roughly 20–26 second intervals. The final completed pass was immediately before the abrupt log end.

This does not prove an access violation by itself; a forced kill after a hung provider produces the same missing footer. It does prove that repeatedly entering the same custom UIA provider is unsafe and unbounded enough to be unacceptable on that field environment.

## H22 behavior

1. On Windows 10 (`build < 22000`) **and** a frozen/PyInstaller runtime, KuGou no longer runs the synchronous in-process HostV2 deep UIA Range scan by default.
2. The Win10 frozen safety profile also suppresses KuGou's hidden-startup Range scan, dense UIA point-probe and shallow pywinauto accessibility wake.
3. Win32 host/title discovery, process liveness, source-affine GSMTC metadata/state, KRC/QRC/LRC fetching, existing numeric/Win32 compatibility clocks and player authority rules remain intact.
4. Other environments retain HostV2 Range. Any single HostV2 UIA call taking >=1.5 s arms a 300 s circuit breaker; repeated quick no-Range misses also arm a shorter breaker.
5. `LIMBUSLYRIC_KUGOU_HOST_V2_UIA_WIN10=1` is an explicit diagnostic opt-in to restore the Win10 frozen HostV2 UIA scan.
6. Python `faulthandler` is attached to the ordinary session log with all-thread stacks. If a future native/runtime fatal fault is catchable by Python's fault handler, the same log should contain thread stacks instead of ending with no diagnostic tail.

## Deliberate non-changes

- No QQ/NetEase clock, seek, liveness, lyric search, presentation, cover color or exit-animation authority was changed.
- No KuGou seek/transport authority was promoted from UI geometry.
- H14 automatic precise-lyric evidence requirements remain unchanged.
- No broad monkey-patch refactor was attempted during this stabilization patch.
