# Variable Font Stability + Shared Frame Pacing R8

- Per-line variable-size mode no longer builds a whole-song Atlas for one transient point size.
- Variable-size history rows freeze their visible transition geometry instead of continuing held shake motion when a new row arrives.
- Fixed-size history motion yields during the existing GUI-late quiet window and uses a bounded secondary cadence under multi-row residency.
- The policy lives in the shared `LyricWindow` / `FadingLine` renderer and is independent of QQ / NetEase / KuGou / Spotify / custom-player clock, search, and seek ownership.
- User-facing support, depth, and frontend copy no longer exposes internal milestone names, Atlas/cache implementation notes, or support resource paths.
