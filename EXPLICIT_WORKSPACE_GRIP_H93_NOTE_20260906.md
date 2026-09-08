# H93 Explicit Workspace Grip

H91/H92 attempted to infer Hero resizing from the page navigation strip and its child buttons. Real
Qt widget event delivery can keep those gestures inside child controls, so the interaction was not
reliable on the user's Windows setup.

H93 now uses an explicit resize grip directly below the page-navigation strip with a deliberately
separated visual size and hit target.

- The layout row is 20 px high. The actual draggable hit target is a centered 72 x 14 px region around the visible 52 x 3 px mark; blank space across the rest of the row is passive.
- Dragging up/down shrinks or expands the Hero / Listening Room region in real time.
- The grip still calls `grabMouse()`, and also installs a temporary application event filter while
  dragging. This second capture path prevents a Windows/Qt pointer-routing quirk from making the
  control appear pressed but immovable after the cursor leaves the narrow mark.
- The Hero minimum is 28 px (near-collapsed) rather than zero. A non-zero floor is intentional
  because historical persistence/start-drag code treats zero as a fallback-to-default value.
- The existing 252 px Hero maximum remains, so expanding the Hero cannot consume the entire settings
  workspace. The grip remains in the settings shell directly below navigation and therefore remains
  available when the Hero is near-collapsed.
- Double-click restores the default Hero height.
- Page navigation buttons remain click-only.
- No player clock, seek, lyric-search, provider identity, renderer, or artwork authority is changed.


## H93F1 real-machine closure

Field feedback showed the H93 visual grip was present but completely immovable. The root cause was
not hit-target size: the main QtCore import omitted `QObject`, while H91/H92/H93 event-filter classes
used `globals().get('QObject', object)`. In the real application they therefore inherited Python
`object`; `super().__init__(grip)` failed and the visible grip remained without an installed event
filter. H93F1 imports Qt `QObject` explicitly and adds a replay assertion for the real import.

The same field pass also closes frontend-palette startup ordering. The persisted H87 Studio/Classic
choice is now committed again from the final H93 init wrapper after all older UI layers have run, and
queued once at 0 ms so earlier queued startup styling cannot overwrite the first visible frame. A
manual frontend-palette change also writes `h87_frontend_theme` immediately before the ordinary
debounced full-config save, preventing a fast restart from falling back to Studio.


## H93F2 compact hit target

Field feedback confirmed the drag path now works, but the H93F1 event filter was attached to the
full-width 20 px row, so touching almost anywhere across that horizontal band could begin a resize.
H93F2 separates layout spacing from interaction ownership: the full-width 20 px row is passive, and
only a centered 72 x 14 px handle receives the drag filter. The visible mark remains 52 x 3 px,
leaving 10 px horizontal and roughly 5 px vertical tolerance around the mark without turning the
whole row into a resize surface. Drag capture, near-collapse limits, double-click restore, and startup
palette restoration are unchanged.
