# H66 — Uninterrupted Blur Exit

H66 closes three field-visible defects left after H65. Capacity-managed blur no longer parks at H64 progress 0.88; the integrated residence clock is allowed to reach 1.0 naturally, so old rows keep becoming more defocused instead of waiting at a fixed optical shelf.

When a row enters the explicit fading lane, H66 scales release duration to the remaining progress instead of spending a complete H62 release interval on only the leftover fraction. A row released around progress 0.88 therefore completes the final 12% in a short continuous tail rather than restarting a multi-second slow phase. H59/H63 first-visible-frame protection is preserved.

The H66 optical curve removes H65's early max-blur plateau. Defocus increases monotonically through progress 1.0. Opacity remains at full visibility until progress 0.94, then uses a back-loaded cubic tail; at the midpoint of that tail visibility remains 87.5%, so the final increase in defocus is still visible before disappearance. No additional raster stage or paint-time filter is introduced.

Field logs also proved that the generic render-pressure valve was directly discarding blur-decay fading rows (`pressure=1 fade_budget=1`, and later `pressure=2 fade_budget=0`). H66 preserves that legacy valve for all non-blur exits, but blur-decay rows are never budget-dropped. Under pressure their remaining-distance release is accelerated with a monotonic progress floor, preventing a row from vanishing mid-effect while still bounding exit-lane residency.

Protected media/provider timing, QQ/KuGou/NetEase transport authority, capacity release ownership, installer entry points and existing legacy method bodies are not modified. H66 is a final runtime presentation layer over H65/H62/H63.
