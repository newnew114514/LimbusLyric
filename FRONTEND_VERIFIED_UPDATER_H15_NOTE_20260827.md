# FRONTEND POLISH R4 + VERIFIED INSTALLER UPDATE H15 — 2026-08-27

## Scope
H15 takes the user-supplied R4 control-panel polish as the presentation baseline and completes the last deferred item from the original UX feature list: verified installer handoff. Player timing/seek/provider authority is unchanged.

## Frontend audit/closure
- The R4 archive changed only the canonical main Python source; all other H14 files were byte-identical.
- Legacy, KuGou golden, RC11, H11, H12, H13, H14 and classic-frontend replays remain protected.
- R4 top-strip navigation, current-page settings search, DIY ordering and reduced-motion shell are retained.
- H12/H13 cards are created after base ControlPanel construction. H15 normalizes their R4 card margins and updates the H12 UI-scale baseline, so changing 100/110/125/150% does not restore old card spacing.
- DIY preview's small header derives from the widget font instead of a fixed 8pt font, so UI scale remains coherent.
- The user-supplied R4 archive intentionally had stale H14 source-lock/manifest hashes after changing the main source. H15 release freeze must regenerate them only after behavior gates pass.

## Verified update contract
- Current version is derived from `LIMBUSLYRIC_BUILD_TAG`; the old hard-coded `1.8.9.133 H12` display is no longer authoritative.
- Version ordering compares the dotted app version first, then H/F stage (for example H10F4 < H14 < H15).
- Supports GitHub Release JSON or a small compatible JSON manifest.
- Automatic execution requires an HTTPS `.exe` installer and an exact SHA-256 digest. GitHub Release assets may provide `digest=sha256:...`.
- If a newer release has no usable digest, H15 only enables the release-page/manual-download path. HTTP/file URLs never become executable update candidates.
- Installer download is daemon/background, capped at 512 MiB, checks the final redirected URL is still HTTPS, writes to `.part`, streams SHA-256, optionally checks expected byte size, then atomically publishes with `os.replace`.
- Only a verified installer is launched. LimbusLyric then uses the existing bounded exit path; the running process never overwrites its own EXE. Installation/replacement/relaunch remains the existing Inno Setup installer's responsibility.
- Download/hash/redirect/oversize behavior is executed by `CHECK_FRONTEND_VERIFIED_UPDATER_H15_REPLAY.py` with fake streaming responses.

## Non-goals
- No code-signing trust root is invented. SHA-256 integrity is only as trustworthy as the configured HTTPS release metadata source.
- No unattended/silent overwrite of the application directory is performed by the main program.
- No QQ/NetEase/KuGou/Spotify clock, seek, identity or lyric-provider authority is changed.

## Release gate
H15 adds `installer/CHECK_FRONTEND_VERIFIED_UPDATER_H15_REPLAY.py`. Canonical suite: **73 gates**.
