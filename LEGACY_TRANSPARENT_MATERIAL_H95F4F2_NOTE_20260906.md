# H95F4F2 · Legacy Transparent Material

H95F4 corrected the shell structure but still looked too much like Studio because its legacy header inherited dark boxed material. H95F4F2 is deliberately visual-only and scoped to `h95f4Frontend="legacy"`.

Changes:
- Legacy window title bar becomes a light translucent overlay with a hairline divider instead of a black framed strip.
- Window buttons are borderless/transparent at rest and only reveal feedback on hover.
- Legacy song status header lets the shared/custom background show through; palette tint remains subtle.
- Native QTabWidget pane is low-opacity and tabs stay transparent with underline selection.
- Legacy setting cards/context strips are lighter translucent layers with hairline separators.
- Modern Studio shell is not restyled by this layer.

No player, lyric, timing, cover, Spotify, Sync Doctor, packaging, or modern Studio behavior is changed.
