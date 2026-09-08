# Runtime UX + Core R2.3.3 paint dependency hotfix — 2026-09-08

Scope is intentionally minimal. A Windows field log from R2.3.2 showed five identical uncaught exceptions from the compact subtitle-region preview: both the legacy `R22RegionPreview.paintEvent()` and compact `R23RegionMiniPreview.paintEvent()` reference `QPalette`, while the canonical `PyQt5.QtGui` import omitted it.

## Fix

- Added `QPalette` to the existing top-level `PyQt5.QtGui` import.
- Added `CHECK_RUNTIME_UX_CORE_R2_3_3.py`, because `py_compile` cannot detect a missing runtime global name. The gate parses the module, proves `QPalette` is imported, proves both preview paint paths are covered, and rechecks the historical runtime wrapper topology.
- No KuGou/QQ clock, lyric search, renderer formula, animation, preview layout, or settings ownership logic is changed.
