# Third-party UI icon attribution — H73

H73's small outline control/navigation icons are visually based on **Tabler Icons**.

- Project: Tabler Icons
- Repository: https://github.com/tabler/tabler-icons
- License: MIT
- Upstream design system: 24x24 outline icons, normally 2px stroke

For LimbusLyric H73, the required shapes are re-expressed with Qt `QPainter` line/ellipse/rect primitives and a lighter 1.55 design-grid stroke. No upstream SVG file is loaded at runtime and no icon font or new package dependency is introduced.

The H73 subset covers: photo-edit/background utility, search, playback/music, typography, sparkles/motion, disc/song, sliders/settings, and standard window controls.
