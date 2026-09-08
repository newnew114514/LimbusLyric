# H45 NetEase clock identity recovery

An anonymous `cloudmusic_detector` placeholder at 0 ms previously became the native primary and
suppressed a progressing GSMTC session. H45 now requires a positive track ID or title at the
adapter boundary and independently checks identity again before granting clock authority. Rejected
samples release fallback and retire stale H35/H38 track witnesses; a legitimate identified track
paused at zero remains valid.

Regression: `installer/CHECK_NETEASE_CLOCK_IDENTITY_H45_REPLAY.py`.

