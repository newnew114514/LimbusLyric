# H95F1 · Adaptive Header / Grip Micro Interaction / Background Frost

- Hero/workspace geometry only: media/seek/provider/lyric timing authority is unchanged.
- Historical untouched 204px Hero default migrates once to 176px; custom heights remain unchanged.
- Hero compression is progressive: spacing/padding and progress rail shrink first, secondary labels retire later, the song title is retained until near-collapse.
- H93 hit target remains compact. The passive row is reduced to 16px and the instructional tooltip is removed. The visible 52x3 mark grows to 56x4 on hover and 60x4 while pressed, with palette-aware brightness.
- Workspace header vertical margins are reduced from the historical 14/12 region to a denser 7/6 baseline (scaled with UI scale).
- Custom panel background adds a persistent 0–100 “背景磨砂” control beside background strength. 0 preserves the previous rendering. Frost is cached in image space via smooth downsample/upscale and does not add blur work to the frame loop.
- Full Settings controls and the top-right Interface popup share the same source sliders/config.
