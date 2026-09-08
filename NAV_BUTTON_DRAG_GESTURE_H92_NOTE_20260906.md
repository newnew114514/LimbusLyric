# H92 Nav Button Drag Gesture

H91 made the top navigation background a vertical workspace splitter, but Qt delivers mouse events on
`播放 / 字幕 / 动效 / 单曲 / 设置` directly to their child buttons. The parent's event filter therefore
never saw those gestures. H92 adds a presentation-only gesture arbiter to the nav children.

- A normal press/release remains an ordinary page click.
- Dominant vertical motion of at least 7 px promotes the gesture to Hero/workspace resizing.
- Promotion clears the button's pressed state and consumes the drag release so the page is not changed.
- Horizontal pointer jitter remains a click candidate.
- H91's empty-background splitter remains unchanged.
- No player clock, seek, lyric search, provider identity, renderer, or artwork authority is changed.
