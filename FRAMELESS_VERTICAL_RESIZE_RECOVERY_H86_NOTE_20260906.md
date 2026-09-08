# H86 Frameless Vertical Resize Recovery

Scope: control-panel window geometry only. Playback, seek, provider, lyric identity, desktop lyric rendering and OBS ownership are unchanged.

## Field failure

A frameless control panel could be resized wider/narrower from the side edges but become effectively impossible to shrink vertically after its bottom edge had been dragged below the screen. The top edge overlaps the custom `PanelTitleBar`; on some Qt/Windows paths the title bar receives the press first and treats it as a window-move gesture instead of native `HTTOP` resize.

This behavior already existed in the H85 baseline; the Lyric Studio frontend restyle did not introduce the underlying title-bar mouse policy.

## H86 closure

- Reserve only the real top resize band (default 8 logical px) before the title-bar move gesture.
- Prefer `QWindow.startSystemResize()` for Top / TopLeft / TopRight.
- Keep a Win32 `WM_NCLBUTTONDOWN` fallback for Windows builds where Qt does not start the system resize.
- Keep the rest of the title bar as the existing move surface.
- Bound the normal control-panel height to the current monitor `availableGeometry().height()` and refresh that bound when moving between monitors.
- On startup, rescue an oversized geometry from an earlier broken session.
- Do not clamp width and do not change page/card scrolling behavior.

## Regression target

The dedicated H86 replay verifies top-edge/corner native resize routing, ordinary title-bar non-interference, and oversized-height recovery.
