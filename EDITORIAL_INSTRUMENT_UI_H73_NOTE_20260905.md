# H73 Editorial Instrument UI

H73 is a presentation-only control-panel refinement. It does not change MediaSessionSync, provider selection, seek authority, lyric timing, overlay placement, exit timing, H72 dirty closure, Atlas rasterization, or installer topology.

## User-facing changes

- The frameless title bar becomes a quieter tool strip. Minimize/maximize/close use small outline icons instead of boxed Unicode glyphs.
- A title-bar `photo-edit` style utility opens a compact **界面背景** popup with enable, image selection, strength, and clear controls. The existing Settings-page background controls stay available as a discoverable fallback.
- Top navigation uses restrained outline icons plus text. Product terminology becomes **播放 / 外观 / 动效 / 单曲 / 设置** while tab indices remain unchanged for config compatibility. The visual order is Playback, Appearance, Motion, Song, Settings.
- The old `字幕` label becomes `外观`; `高级` becomes `设置`; `单曲DIY` becomes `单曲`.
- The old `模式：中文/英文` renderer switch is relabelled **退场质感：完整字形 / 轮廓余韵**. Stored data remains `chinese/english`, so old configs and presets continue to load unchanged.
- Visible section headings beginning with Hxx generation tags have that implementation prefix removed. Hxx markers remain in source, logs, notes, and gates.
- Settings search gains a small search icon but intentionally remains current-page filtering in H73. The tooltip states that scope explicitly.

## Icon source / dependency policy

The visual language is based on the Tabler Icons 24x24 outline system (MIT). H73 re-expresses the small subset it needs as direct Qt `QPainter` primitives in the main source rather than shipping SVGs or adding QtSvg/runtime asset dependencies. See `THIRD_PARTY_UI_ICONS_H73.md`.

## Safety boundaries

- No media/provider/seek methods are called by the H73 block.
- No new worker threads, network calls, QImage filtering, or overlay drawing hooks are added.
- H73 wraps `PanelTitleBar.__init__`, `PanelTitleBar.sync_window_state`, and `ControlPanel.__init__` only.
- Existing background persistence remains owned by `_choose_background_image`, `_clear_background_image`, `_apply_background`, and existing config-save code.
- Existing tab indices remain 0..4; only presentation order and labels change.
