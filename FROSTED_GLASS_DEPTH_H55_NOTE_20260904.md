# H55 · Frosted Glass Depth

H54 fixed the ownership model: each lyric samples one immutable random depth layer and keeps it for its whole lifetime. Field review then showed the optical separation was too conservative: turning depth on could look almost the same as turning it off.

H55 keeps H54's random fixed layer model and strengthens only the optical presentation. The curve is nonlinear: layer 1 is untouched; middle layers remain readable; layers 5/6 rapidly lose crisp-core opacity into a wider multi-direction Atlas bloom. At the existing default 55% strength, layer 6 uses roughly a 14 px diffusion radius, 8 Atlas passes and about a 15% crisp core. At 100%, the deepest layer can exceed 20 px diffusion with only an ~8% crisp core, intentionally approaching text seen through thick frosted glass.

No QImage, Gaussian blur or QGraphicsBlurEffect is added. The same immutable glyph Atlas is redrawn at stable subpixel offsets. Existing user glow therefore spreads naturally in far layers, while glow-off text still gets a restrained lens-like halo.

Performance closure: active rows already carry renderer pressure into H54. H55 also gives history rows a weak owner-window reference so their frost follows the same pressure policy. Pressure level 1 caps the effect to at most four passes and restores more crisp text; pressure level 2 disables all extra frost passes and draws the authoritative sharp Atlas path.

H53 center avoidance, H54 random fixed Z, H51 exit/font/screen customization, and all provider/transport logic are unchanged.
