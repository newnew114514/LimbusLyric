# H53 Presentation Depth + Center Avoidance

H53 is presentation-only and is layered on top of H52. It does not modify playback clocks, provider identity, seek authority, automatic lyric transactions, or the H52 KuGou build-26200 safety policy.

## Fixed: center frequency

H51 had two practical defects. A persisted `0` was loaded through an `or 100` expression, so it became 100 after restart. At runtime the avoidance path only re-ran the normal placer a few times and then intentionally accepted a center placement. It also checked only the line center, so a long line whose anchor was outside could still cross the center of the screen.

H53 preserves zero literally. For a row selected for avoidance, the full center rectangle is injected as a high-weight obstacle into the existing balanced placement scorer. The final visible lyric footprint is checked; if it still intersects the center zone, a deterministic minimum-shift closure moves the whole footprint outside while scoring real subtitle overlap and off-screen cost. At 0%, every new row takes this strict path. At 100%, the original full-screen balanced placement is unchanged.

## Fixed: duplicate exit demonstrations

H51 `per_char` used a right-to-left character rank, so on ordinary horizontal lyrics it looked nearly identical to `wipe_rtl`. H53 keeps the same batched `QPainter.PixmapFragment` renderer but gives `per_char` a stable per-row shuffled rank. The result is an organic staggered glyph dissolve, while left-to-right and right-to-left remain spatial wipes. No rectangular clipping returns.

## Added: 3D depth stack

3D depth is opt-in and defaults off. The active lyric remains the crisp foreground. Held/fading historical rows receive increasing depth levels by age. A farther row is scaled toward the viewport center with one QPainter matrix transform; the maximum recession is bounded and controlled by a 0–100 strength slider and a 2–6 layer selector. No Gaussian blur, new glyph rasterization, or extra provider/timing work is added to the frame loop. Existing perspective transforms and Atlas/fragment rendering remain in use.
