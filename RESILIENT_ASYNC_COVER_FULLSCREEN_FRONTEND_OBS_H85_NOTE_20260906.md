# H85 — Resilient Async / Instant Cover / Fullscreen / Frontend / OBS

H85 keeps the H84 player-epoch publication firewall and moves only the slow Windows GSMTC manager/MediaProperties awaits into bounded single request slots. Position/UIA/native sampling continues while a WinRT request is slow. A cancelled native request retains its slot until it actually completes, preventing unbounded task multiplication. A truly cancellation-resistant native awaitable can still delay final `asyncio.run()` teardown; H85 does not claim to solve that operating-system/runtime limitation.

Cover-follow now persists validated `#RRGGBB` accents for 90 days (bounded to 256 entries). On a known track, the cached accent is preseeded before the historical per-track style application, so startup does not intentionally render a default-color line before switching. Unknown tracks start the existing background cover resolver immediately instead of waiting for the 1100 ms periodic timer.

The lyric HWND reasserts `HWND_TOPMOST` with `SWP_NOACTIVATE` after show/foreground transitions and periodically while a foreground window matches its monitor bounds. No input injection, focus stealing, or game hooking is used. True exclusive fullscreen can bypass ordinary desktop windows and is not guaranteed.

Frontend page switching skips the H75 all-page search scan when the search box is empty, caches card search text while search is active, coalesces duplicate H80 stage synchronization, and shortens only the lightweight nav-indicator motion. Visual polish remains stylesheet-only; no new blur/shadow effects are added to the control panel.

The existing H13 OBS mirror remains presentation-only and owns no media clock. H85 samples it at ~30 fps but captures pixels only when the source lyric window has repainted, changed its bounded visual region, geometry, or opacity. OBS users should select the stable `LimbusLyric OBS Lyrics` window with Window Capture. Real OBS/Windows capture still requires end-user machine validation.
