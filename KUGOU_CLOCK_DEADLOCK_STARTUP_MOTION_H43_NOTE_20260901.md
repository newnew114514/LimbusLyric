# H43 KuGou clock-deadlock + startup-motion safety

Field logs from packaged Windows build 26200 showed KuGou PLAYING while GSMTC position remained 0. Startup late-attach correctly refused synthetic zero, but HostV2 had not yet completed formal proof, leaving instrumental presentation at position 0 indefinitely. H43 gives instrumental cards a presentation-only monotonic clock and permits the first non-zero plausible HostV2 Slider sample to seed display-only position before formal proof. Neither path grants duration or seek authority.

The same logs repeatedly raised 0x8001010d at StartupMotion.show_centered -> QWidget.show. Packaged Windows therefore skips the cosmetic StartupMotion stage and constructs the normal panel directly.
