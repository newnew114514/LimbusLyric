# Frontend Runtime Restore R1 audit — 2026-09-08

This restore build deliberately uses S2 as the runtime base and retires the S3/S4/S4.1 wrapper-consolidation experiment.

Reason: RC11's UI/animation behavior depends on runtime wrapper installation semantics. S3/S4 mechanically consolidated several wrapper chains and release replays did not prove whole-program equivalence. Real-user testing showed missing frontend transitions, exit effects and other presentation features.

R1 policy:
- preserve the original RC11 runtime installation chains for UI/render/playback methods;
- keep the additive S1/S2 lyric core, local lyric formats, provider/playback contracts and bounded fault journal;
- do not consolidate ControlPanel.__init__, LyricWindow.paintEvent, FadingLine.draw, LyricWindow._make_history_line, MediaSessionSync bind/snapshot, or LyricSearchEngine.search;
- no visual redesign and no default-style changes.

Static AST comparison against the uploaded audited RC11 baseline showed exact right-hand-side sequence parity:
- ControlPanel.__init__: 54 / 54 wrappers, exact sequence match
- LyricWindow.paintEvent: 10 / 10 wrappers, exact sequence match
- FadingLine.draw: 17 / 17 wrappers, exact sequence match
- LyricWindow._make_history_line: 18 / 18 wrappers, exact sequence match
- LyricSearchEngine.search: 5 / 5 wrappers, exact sequence match
- MediaSessionSync.bind_track: 6 / 6 wrappers, exact sequence match
- MediaSessionSync.snapshot: 4 / 4 wrappers, exact sequence match
- LyricWindow.showEvent: 1 / 1 wrapper, exact sequence match

This is a runtime-structure parity audit, not a substitute for Windows visual testing.
