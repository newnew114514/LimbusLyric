# H89 Collapsible Preview / Resize Stability / Micro Interactions

Field feedback after H88 showed four presentation issues:

1. the fixed Subtitle/Motion preview still consumed too much vertical workspace;
2. the section chips looked decorative because jumps had no persistent/visible section state;
3. H86 could fight Windows during an active top-edge native resize because moveEvent performed an immediate rescue resize;
4. H87/H88 page snapshots could briefly duplicate old/new content and spent frame budget compositing large pixmaps.

H89 is presentation/shell-only. It does not change player transport, seek, lyric search, provider identity, timing authority or desktop lyric rendering.

## Changes

- Preview has only two states: a 48 px disclosure rail showing `预览`, or the existing compact ~92 px live preview. The old large-preview mode is retired.
- Preview open/close animates maximumHeight over 168 ms and persists as `h89_preview_open`.
- Section navigation is re-homed immediately after the workspace header, uses active-state underlines, follows scrolling, and briefly highlights the target settings card after a jump.
- H87/H88 workspace screenshots are retired. Page changes use a small paint-only focus veil plus existing semantic header/nav motion; no page pixel capture is used.
- Manual `展开歌词文本` / `收起歌词文本` now uses height + opacity disclosure rather than instant show/hide.
- H86 historical code remains untouched, but its runtime helper ownership is replaced: no in-drag `setMaximumHeight()/resize()` rescue. H89 waits until the mouse is released and the native geometry transaction settles, then clamps only vertical size/position to the monitor work area.
- Windows top-edge fallback uses one posted `WM_NCLBUTTONDOWN` transaction rather than mixing Qt `startSystemResize()` with a Win32 fallback for the same press.
- Minimum control-panel height is reduced from the historical 540 px runtime constraint to 460 px; settings pages remain scroll-based. Width behavior is unchanged.

## Expected result

- Subtitle/Motion pages dedicate substantially more height to actual settings when preview is closed.
- Section navigation provides visible feedback instead of appearing inert.
- Switching pages no longer shows temporary duplicated page/footer imagery from frozen snapshots.
- Top-edge resize should no longer jump the frameless panel while dragging.
