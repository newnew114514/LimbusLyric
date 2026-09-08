# H81 CURRENT CHECKPOINT NOTICE — 2026-09-05

Current release candidate: H81 LYRIC IDENTITY FIREWALL. Read `LYRIC_IDENTITY_FIREWALL_H81_NOTE_20260905.md` first, then H80/H79/H78 notes. Canonical suite: 143 gates. H81 fixes the observed 203s lyric / 239s QQ player authority inversion, covers fast-stage hidden candidate durations, and closes cross-player lyric-provider transport leakage plus the Spotify zero-witness gap without modifying source-locked player clocks, KuGou/NetEase core clock+seek paths, H80 presentation, or packaging commands.

# H80 CURRENT CHECKPOINT NOTICE — 2026-09-05

Current release candidate: H80 STABLE STUDIO STAGE + LANDMARK MICRO MOTION. Read `STABLE_STUDIO_MICRO_MOTION_H80_NOTE_20260905.md` first, then H79/H78/H77/H76 notes. Canonical suite: 142 gates. H80 retires whole-page snapshot transition, re-homes the mature H74 preview cards into a fixed Studio Stage, and animates only navigation/workspace/first-section landmarks. Player/provider/seek/blur/config authority is unchanged.

# H77 CURRENT CHECKPOINT NOTICE — 2026-09-05

Current release candidate: H77 APPLICATION SHELL + INSPECTOR SYSTEM. Read `APPLICATION_SHELL_INSPECTOR_H77_NOTE_20260905.md` first, then H76/H75/H74/H73 notes. Canonical suite: 139 gates. H77 is shell/presentation only; H12 scale/background widgets remain config owners and player/provider/seek/desktop-exit authority remains unchanged.

# H75 CURRENT CHECKPOINT NOTICE — 2026-09-05

The current release candidate is H75 INFORMATION ARCHITECTURE + SPOTIFY PARITY, not the older H12/H13-era candidate described by some historical sections below. Start with `INFORMATION_ARCHITECTURE_SPOTIFY_PARITY_H75_NOTE_20260905.md`, then H74/H73/H72 notes. The canonical suite now registers 137 gates. H75 keeps ALL plus independent QQ / NetEase / KuGou / Spotify per-song visual slots and gives Spotify an independent display offset. Historical transport/provider constraints below remain authoritative unless a later Hxx note explicitly supersedes them.

# H22 stabilization handoff

Current field hardening: Windows 10 frozen KuGou deep-UIA safety mode + slow-provider fuse + native fault trace. See `KUGOU_WIN10_CRASH_HARDENING_H22_NOTE_20260828.md`. Do not re-enable in-process Win10 KuGou HostV2 deep UIA by default without new field evidence.

# H21 FINAL HANDOFF — KUGOU IDENTITY + COVER UI — 2026-08-28

Current candidate: H20 presentation/packaging baseline + H21 KuGou real-machine identity corroboration. Dedicated gate: `installer/CHECK_KUGOU_IDENTITY_COVER_UI_H21_REPLAY.py`. Canonical suite: **79 gates**. Read `KUGOU_IDENTITY_COVER_UI_H21_NOTE_20260828.md` first.

Protect every existing H20/H19/H18/H17/H16/H15/H14 behavior and all player clock/Seek authority. H21 is limited to conflicting KuGou identity corroboration, reuse/rescue of independent Host-V2 duration evidence for KRC version selection, and physical relocation of the existing cover-follow checkbox.

------------------------------------------------------------------------

# H19 FINAL HANDOFF — COVER FOLLOW + MIRRORED EXIT — 2026-08-28

Current candidate: H18 liveness corroboration + H19 presentation closure. Dedicated gate: `installer/CHECK_COVER_EXIT_H19_REPLAY.py`. Canonical suite: **77 gates**. Read `COVER_EXIT_MIRROR_H19_NOTE_20260828.md` first.

Protect all existing H18/H17/H16/H15/H14/H13/H12/H11 behavior and every player authority. H19 may change only cover metadata/color presentation and fading-row exit presentation. Do not move H19 after the H14 extraction marker without updating the H14 replay boundary, and never update source locks merely to silence a behavioral regression.

------------------------------------------------------------------------

# H18 FINAL HANDOFF — LIVENESS CORROBORATION — 2026-08-28

Current candidate: H16 presentation runtime wiring + H17 reliability closure + H18 false-dead liveness corroboration. Dedicated gate: `installer/CHECK_LIVENESS_CORROBORATION_H18_REPLAY.py`. Canonical suite: **76 gates**. Read `LIVENESS_CORROBORATION_H18_NOTE_20260828.md` first.

Protect all existing H17/H16/H15/H14/H13/H12/H11 behavior and every player authority. H18 is limited to corroborating negative liveness observations, negative startup/dwell gating, and strict-active GSMTC positive presence veto/rescue.

------------------------------------------------------------------------

# H16 FINAL HANDOFF — UX RUNTIME WIRING — 2026-08-28

Current candidate: H15 R4 frontend/updater baseline + H16 presentation runtime wiring. Dedicated gate: `installer/CHECK_UX_RUNTIME_WIRING_H16_REPLAY.py`. Canonical suite: **74 gates**. Read `UX_RUNTIME_WIRING_H16_NOTE_20260828.md` first.

Protect all existing H15/H14/H13/H12/H11 behavior and all player authority. H16 may own only presentation style/exit/cover/UI wiring. Never regenerate legacy/golden/source locks merely to silence a failing behavior gate.

------------------------------------------------------------------------

# H15 FINAL HANDOFF — FRONTEND POLISH R4 + VERIFIED INSTALLER UPDATE — 2026-08-27

Current candidate: user-supplied R4 frontend diff on top of frozen H14, plus a narrow H15 update/install handoff closure. H15 does not change player or lyric clock authority.

Before editing, run all **73** entries in `installer/RELEASE_GATE_SUITE.tsv`. H15 dedicated gate: `installer/CHECK_FRONTEND_VERIFIED_UPDATER_H15_REPLAY.py`. Read `FRONTEND_VERIFIED_UPDATER_H15_NOTE_20260827.md` first.

Important H15 invariants:
- Keep the R4 top-strip navigation/current-page search and do not use frontend work as a reason to alter provider timing.
- Runtime-added H12/H13 settings cards must remain in the same UI-scale baseline as the R4 cards.
- Current update version comes from `LIMBUSLYRIC_BUILD_TAG`, not a stale H12 literal.
- Auto-install requires HTTPS installer + SHA-256. Without a digest, only the HTTPS release page may be opened.
- Streamed download is bounded, writes `.part`, verifies size/hash, and atomically publishes before execution.
- The main process launches the existing installer and then follows the H11 bounded exit path; it never overwrites its own running EXE.
- Do not change source locks/manifest simply to hide a frontend or H15 regression.

------------------------------------------------------------------------

# H14 FINAL HANDOFF — AUTO PRECISION DEADLINE — 2026-08-26

Current candidate: H13/H12/H11 baseline + H14 outer lyric-retrieval closure. Real H10F4 evidence showed a KuGou progressive auto-search whose fast LRC was visible in ~2.2s while the precise/KRC enhancement remained alive for ~204.8s. H14 bounds that enhancement without changing any player clock or seek authority.

Before editing, run all **72** entries in `installer/RELEASE_GATE_SUITE.tsv`. H14 dedicated gate: `installer/CHECK_AUTO_PRECISION_DEADLINE_H14_REPLAY.py`. Read `AUTO_PRECISION_DEADLINE_H14_NOTE_20260826.md` first.

Important H14 invariants:
- Only automatic KuGou precise enhancement is budgeted: 22s cooperative total, max 2 in flight.
- Automatic KuGou MSAA version-duration evidence is presentation/version-selection evidence only: 1.25s wait, max 1 possibly stuck probe.
- If that version proof times out, discard precise/KRC enhancement and keep already-displayed ordinary lyrics. Never accept an unproven same-title precise payload.
- `progressive_keep_fast` requires the fast stage to actually own the current loaded track.
- Manual fetch, QQ/NetEase search, KuGou transport/Host/seek authority, H11-H13 and V28/V29 remain unchanged.
- Do not update locks or allow-lists merely to silence a red gate.

------------------------------------------------------------------------

# H13 FINAL HANDOFF — OUTPUT / DIY / SPOTIFY — 2026-08-26

Current candidate: H12/H11 baseline + H13 outer extensions. H13 adds three exact track-owned lyric payload slots, a presentation-only OBS mirror, and Spotify as a strict Windows local-GSMTC built-in. It does **not** replace QQ Software-2, KuGou golden transport, NetEase native authority, V28/V29 contracts, or H11/H12 responsiveness/presentation closures.

Before editing, run all **71** entries in `installer/RELEASE_GATE_SUITE.tsv`. H13 dedicated gate: `installer/CHECK_OUTPUT_DIY_SPOTIFY_H13_REPLAY.py`. Read `OUTPUT_DIY_SPOTIFY_H13_NOTE_20260826.md` first. Never regenerate legacy/golden/source locks just to make a red gate green.

Important H13 invariants:
- Runtime H13 closures must stay before the `__main__` startup block.
- User lyric content is exact song+artist ownership; do not widen it to the legacy style matcher.
- Spotify playback identity/status/position/duration are player-owned local GSMTC evidence. QQ/NetEase/KuGou may supply lyrics only; their UIA clocks must not become Spotify transport authority.
- OBS output is presentation-only and owns no second MediaSync.
- H13 controls participate in H12 UI scaling.
- Automatic in-place EXE replacement remains deferred.

------------------------------------------------------------------------

# H12 FINAL HANDOFF — UX EXTENSIONS — 2026-08-26

Current candidate: H11 responsiveness baseline + H12 presentation/control-panel extensions. H12 adds UI scaling, lyric opacity, continuous global weight, bounded micro-jolt shake, cover-follow color, independent exit effects, safe Windows capture exclusion, and HTTPS update checking. It does not change player time/seek/provider authority.

Before editing, run all 70 entries in `installer/RELEASE_GATE_SUITE.tsv`. H12 dedicated gate: `installer/CHECK_UX_EXTENSIONS_H12_REPLAY.py`. Do not regenerate legacy/golden locks to hide regressions.

Deferred by design: dedicated OBS mirror window, Spotify provider adapter, precise/classic/translation per-song lyric slots, and automatic in-place EXE replacement. See `UX_EXTENSIONS_H12_NOTE_20260826.md`.

------------------------------------------------------------------------

# H11 final addendum — POST-RELEASE RESPONSIVENESS — 2026-08-25

This addendum has precedence over older root-level handoff wording when it concerns the post-release issues below. Historical sections remain provenance.

## Evidence boundary
The H11 fixes were re-derived from the bundled raw user logs and the current H10F4 source. Old report conclusions that were not supported by the source were explicitly discarded. In particular, `player=QQ音乐 | source=酷狗` is a legal cross-source lyric configuration, lack of a search log after an identity prompt is not proof of a swallowed click, and a newly observed long `paintEvent` may temporarily coexist with older frame/timer maxima.

## H11 targeted closures
- GUI snapshot callers no longer execute QQ gesture or NetEase click/hover control work synchronously. Requests are coalesced onto isolated daemon workers; a stuck helper cannot make the caller wait and watchdog telemetry can fire before the helper returns.
- Manual lyric fetching is a generation-scoped asynchronous transaction. Precise mode can display ordinary lyrics first and upgrade later; stale/late results are rejected and GUI waiting is bounded.
- H10 liveness multi-sample death proof remains. Toolhelp observations are now disposable/quarantined after a deadline, followed by a separately bounded `tasklist` observation. A nonzero/blank `tasklist` result is UNKNOWN, not dead. Late Toolhelp answers from a timed-out observation are stale.
- QQ `status=unknown` receives only a narrow cold-start fallback from repeated high-confidence `qq-time-pair-validated` advancement. Formal Software-2/seek/hover authority is not replaced.
- Presentation ownership belongs to the confirmed current track. Failed new-track fetches cannot restart an older payload; successful later tracks release any prior blank/suspension state.
- `trans_only` is persistent user preference. A no-translation result affects the current presentation, not the checkbox/config value. Existing precise-vs-translation mutual exclusion is otherwise retained.
- Fresh-but-malformed KuGou HostV2 window titles are not canonical identity authority when more credible metadata exists. Host discovery misses use bounded backoff; force events can bypass it.
- Atlas inflight/performance fuse and proven slow paint can enter a cheap presentation fallback. This changes visual decoration/cadence under pressure, not lyric-time authority.
- Exit uses bounded shutdown and a last-resort process-exit watchdog so an unreturning helper/provider cannot keep the user-visible application indefinitely resident.

## Release contract
- Canonical suite: 69 entries, including H11 plus V14/V16/V17 which were previously present but omitted from the TSV.
- `CHECK_LEGACY_BASELINE_INTEGRITY.py`: 481 unchanged old functions locked at this candidate.
- `CHECK_KUGOU_GOLDEN_BASELINE.py`: 22 source-locked KuGou methods.
- H11 dedicated executable replay: `installer/CHECK_POST_RELEASE_RESPONSIVENESS_H11_REPLAY.py`.
- Do not weaken release gates or update baseline hashes simply to make an unreviewed diff pass.

## Remaining evidence limitation
The candidate can be source-audited and fault-injection/replay tested in this environment, but QQ/NetEase/KuGou Windows UIA/GSMTC behavior and the Windows installer cannot be truthfully called real-machine tested here. Treat future real-user logs as higher-value evidence for environment-specific failures; do not preemptively redesign authority without such evidence.

------------------------------------------------------------------------

# Codex handoff — v1.8.9.133 RC11 UX/SCRIPT POLISH 20260817

Treat this directory as an RC candidate, not a refactor playground. First audit; do not modify hashes/allow-lists just to make gates green.

## QQ SAIKAI duration arbitration
- Sandbox SAIKAI exposed a false QQ UIA `04:25` duration while identity-matched system transport already reported ~323.946s.
- `_qq_transport_duration_evidence()` is for lyric-version selection only and does not become playback authority.
- Do not widen provider duration tolerances.

## Single-song DIY contract
- Exactly one visible row per song identity.
- Each song has two application modes: `ALL` (one unified style for every supported player) and `per_player` (independent `qq`, `netease`, `kugou` slots).
- The song-row badge is a real button that toggles `ALL` / `四家独立`; the “编辑播放器” combo also exposes `ALL` and stays synchronized with that mode.
- Switching modes must preserve the inactive side. ALL -> per-player may seed only missing provider slots from ALL; existing QQ/NetEase/KuGou/Spotify payloads must never be overwritten. Per-player -> ALL may seed a missing ALL payload from one existing provider, but must not delete provider slots.
- Runtime selection follows the actual player/transport. In ALL mode it uses `rules["all"]`; in per-player mode it uses only the actual player's slot.
- Saving/quick-editing `ALL` writes only `rules["all"]`; saving/quick-editing a provider writes only that provider slot.
- Config schema v5 restores first-class ALL while preserving schema-v4 per-player rows as per-player by default.
- Row must remain readable and retain direct font and color/effect editing for the currently active mode.
- Color/effect dialog includes text color, shadow, outline/stroke width and glow toggles/colors.

## Custom font contract
- Subtitle page exposes `导入字体` for TTF/OTF/TTC.
- Imported files live under `%LOCALAPPDATA%\LimbusLyric\fonts` and are registered with `QFontDatabase.addApplicationFont` for the app only.
- Startup reloads this directory before font selectors are built.
- Do not install fonts into Windows or copy them into the application install directory.

## Theme/UI contract
- Public Limbus theme selection/import tools/tray menu remain removed; standard interface is forced.
- Perspective X/Y/horizontal compensation remain user adjustable.

## Logging/config/release contract
- Config schema is `5`.
- Preferred logs: `%LOCALAPPDATA%\LimbusLyric\logs`, max 5 sessions; long current logs trim in background.
- `installer/LimbusLyric.spec` remains byte-for-byte locked to SHA256 `a60e563c0ae3a97b259cb19732e5ebd6bb534cf5640f0c97338500d714d535ec`.
- `CHECK_RC_AUDIT_CLOSURE_REPLAY.py`, `CHECK_KUGOU_AUDIT_CLOSURE_REPLAY.py`, `CHECK_RC_AUDIT_RISK_DIAGNOSTICS.py`, `CHECK_PACKAGING_STRUCTURE.py`, existing QQ authority gates, KuGou golden gates, Codex protected behavior, packaging contract and release invariants must remain green.

## Do not casually touch
- NetEase native-log authority/seek path.
- QQ GSMTC guard, Text-boundary fallback, seek stale-echo/hover quarantine, RangeV2 fuse.
- KuGou Host V2 + UIA Slider/RangeValue authority and 21 golden methods.
- Shared renderer based only on isolated GUI gap counters.

## 2026-08-17 UX / script / instrumental addendum
- This candidate is based on the user-tested V7 KuGou GUI-stall fix. Do not reintroduce synchronous `tasklist` into the GUI snapshot/gesture path.
- `软件教学` opens the author's Bilibili page with `QDesktopServices.openUrl`; this is UI-only.
- Korean change is classification-only: precomposed Hangul syllables may enter the existing presentation cascade inside a real provider token. No new lyric timestamps or Korean-specific authority/timing constants are introduced. Complex shaping scripts remain provider-atomic.
- Instrumental boilerplate is replaced only in the renderer payload by a compact title/artist card and auto-hidden after the presentation hold. The original provider text remains the click-timeline input. Do not turn instrumental detection into track/clock authority.
- DIY live preview, per-category reset buttons, imported-font manager, and current-track status card are presentation/config UX only.
- Slow-call telemetry in `MediaSessionSync.snapshot` / `LyricWindow.check_lyric_time` is observational. It must not change provider return values, thresholds, locks, seek state, or authority.
- Dedicated gate: `installer/CHECK_UX_SCRIPT_INSTRUMENTAL_REPLAY.py`.
- For any follow-up review, audit this UX/telemetry diff narrowly. Do not refactor the three player adapters unless a new deterministic failure or Windows log proves a problem.

## 2026-08-17 player-scoped late-attach closure
- A cached loaded track belongs to `_loaded_player`; it is not proof that a newly selected different player has already attached.
- On a built-in player switch, zero-touch first-attach is therefore computed from the actual selected player, never from lyric source and never from the mere presence of `_loaded_track_key`.
- Cross-player first attach passes `startup_existing=True` and zero detection latency to the existing QQ/KuGou witness lanes. Same-player ordinary track changes keep their historical provisional behavior.
- This closure changes no QQ/NetEase/KuGou clock, seek, duration, RangeValue, Host V2, GSMTC, native-log, golden, or lyric-parser function.
- Dedicated behavioral gate: `installer/CHECK_ALL_PLAYER_LATE_ATTACH_PLAYER_SCOPE_REPLAY.py`.

## 2026-08-17 V12 instrumental fast-path closure
- User runtime V11 proved KuGou reversible mojibake recovery was working, but repaired text still carried `id00000000qqtotal...` bookkeeping ahead of `纯音乐请欣赏`, so exact presentation classification missed. V12 strips only a bounded list of leading numeric provider metadata tokens after reversible repair.
- NetEase and KuGou pure-music tracks were paying 2–4 extra seconds in the cross-provider precision ladder after the selected provider had already returned a pure-music placeholder. `LyricSearchEngine.search` now treats a confirmed primary instrumental payload as terminal for lyric-quality enhancement and skips foreign provider probes.
- This is a reviewed retrieval-only change. It does not change player clock/seek authority, KuGou Host V2/RangeValue, QQ GSMTC/UIA arbitration, or the 21 KuGou golden methods.
- Runtime marker: `INSTRUMENTAL-RUNTIME-V12`. Fast closure diagnostic: `纯音乐主源快速收口`.

## 2026-08-17 V14 lyric-pipeline stability closure
- Keep transport/player identity separate from lyric-payload provenance. Foreign lyric providers may contribute text, but may not become playback/seek authority.
- Cross-provider instrumental classification is performed on the returned payload with its actual payload source before session caching; sparse provider placeholders must not be cached as ordinary QQ/NetEase/KuGou lyrics merely because the active player differs.
- Provider attempts use isolated metadata frames so one attempt cannot leak payload metadata into the next candidate.
- On a source-switch race with the same current track transaction, requeue lyrics for the current source only (`media-rebind=0`); do not call MediaSync.bind_track from this recovery.
- While a new auto-track lyric transaction is pending, do not relaunch a stale loaded track.
- Unknown-duration KuGou instrumental cold-start evidence is display-eligible but not sticky-session-cache eligible until duration identity is proven.
- Inactive KuGou mouse-event cleanup logging is coalesced only; queue draining and the 21 source-locked KuGou methods remain unchanged.
- Runtime marker: `INSTRUMENTAL-RUNTIME-V14`. Dedicated replay: `installer/CHECK_LYRIC_PIPELINE_V14_REPLAY.py`.


## V24P1 packaging transient isolation (2026-08-18)
Runtime source is unchanged from V24. A Windows build exposed that `CHECK_PACKAGING_STRUCTURE.py` did not exclude `.build_installer_venv_ascii`, even though cache-clean and release-invariant gates did. The packaging path policy is now centralized in `installer/PACKAGING_PATH_POLICY.py` and covered by `CHECK_PACKAGING_BUILD_ARTIFACT_ISOLATION_REPLAY.py`. The replay verifies known build/runtime transients are ignored while project-source Python caches and unknown undeclared outputs remain fatal.


## V25 evidence epoch closure (2026-08-18)
- Sandbox proved QQ MediaProperties can lead TimelineProperties: new title `夜、萤火虫和你` arrived while old 271016ms duration remained, then the correct 188943ms timeline arrived one second later. V25 quarantines unchanged pre-bind duration evidence across bind.
- QQ/KuGou `media_metadata_mono` now means actual identity change for both players.
- KuGou first-attach can use a plausible Host-V2 native-range position as display-only provisional position before duration proof, preventing multi-second 0ms jumps.
- Formal Host-V2 duration/absolute clock/Seek and QQ Software-2 authority remain unchanged.
## V26 evidence epoch2 + font/glow (2026-08-18)
- Host log proved KuGou Host V2 Range evidence could cross both player and identity boundaries: QQ 160000ms was temporarily carried into KuGou, an unbound 85050ms Range was later attached to `Something Just Like This`, and a just-bound new song could be mislabelled as same-track restart. V26 adds player/identity/Range/transport ownership epochs and requires post-bind Range re-observation.
- Subtitle font UI removes the recommendation button, adds global + per-song DIY bold/italic, and routes all global/DIY glow through one soft multi-layer halo helper.



## V28 precision visual handoff (2026-08-18)
- Host V27 log proved the existing `visual_preserved=1` seamless upgrade still allowed the next precise animation tick to recompute a smaller `char_index`, producing a visible ordinary-prefix -> retract -> precise-retype sequence.
- V28 treats an already-started current row as a presentation transaction. `upgrade_lyric_timeline_preserve_visual()` stores the precise timeline in `_precision_handoff_pending` instead of replacing the active fallback timeline once `char_index > 0`.
- The current row is matched to the precise book by normalized row text where possible. Ordinary LRC cannot start a second row while the lease is active. Once a matched fallback row is fully revealed, precision may be installed early with `_precision_handoff_visible_floor` holding the complete row; otherwise the swap waits for the next precise row boundary.
- `_activate_precision_handoff()` installs precision atomically at the safe boundary. Accepted seek intent bypasses the lease and forces immediate precise rebuild. Zero-visible-glyph upgrades remain immediate.
- This is presentation-only. `MediaSessionSync` / `LyricSearchEngine` authority is not intentionally modified. Dedicated gate: `installer/CHECK_LYRIC_PIPELINE_V28_PRECISION_VISUAL_HANDOFF_REPLAY.py`.
- V28 also expands placement candidates only in crowded scenes (3+ predictive obstacles) to reduce the remaining ~9% overlap fallback observed in the V27 host log.

## V29 transport generation + burst admission (2026-08-18)
- V28 host log confirmed Precision Visual Handoff is healthy and source-locked unchanged in V29.
- KuGou playlist rows can be distinct playback instances while exposing identical title/artist. V29 therefore adds a play-instance `kugou_transport_generation` below song identity. It never changes lyric/provider identity by itself.
- Hidden same-title rollover inference is deliberately narrow: known duration, raw Windows status `playing`, local Rail clamped at end, 3 observations spanning >=1250ms, and neither Host V2 nor visual rail fresh. A real Host/visual rail remains authoritative and vetoes this inference.
- When hidden rollover is proved, the Rail reanchors to the inferred continuation dwell (capped 2500ms) rather than literal zero so proof latency does not make lyrics late. Provider search/DIY/song identity remain bound and cached.
- Extreme dense bursts retire only rows already in `fading_lines` before placement. Current text and readable `history_lines` are preserved; ordinary cadence does not enter this admission path.
- Atlas pixels/effects are unchanged. V29 only drops stale queued atlas results before QPixmap conversion, reserves existing LRU capacity before conversion, and records install stages (convert/meta/evict/cache/activate) for Windows diagnosis.
- Expected requests timeout failures are logged as a concise network timeout summary. Unexpected provider exceptions still keep full traceback.
- Dedicated gate: `installer/CHECK_LYRIC_PIPELINE_V29_TRANSPORT_GENERATION_BURST_ADMISSION_REPLAY.py`.

## H23 Win10 compatibility / reproducible-build closure (2026-08-29)
- Win10 (<22000) + frozen + KuGou now decides the safe profile before `PlayerUiPositionReader._ensure_desktop()`, so pywinauto UIA Desktop is not initialized on the field-risk path. The same exact profile also skips the in-process comtypes/MSAA playback-clock and version-duration tree traversals.
- H22 deep HostV2/hidden-range/point-probe/wake guards remain defense-in-depth.
- Known-good direct UI/COM runtime versions are pinned and the one-click builder requires Python 3.12.x, with a post-install runtime-profile verifier.
- Do not globally force COM STA/MTA; other WinRT/pycaw/player paths share the process.
- Process-isolating UIA remains deferred architecture work, not part of this stability release.

## H24 Win10 runtime safety
See `WIN10_RUNTIME_SAFETY_H24_NOTE_20260829.md`. H24 is a narrow late-wrapper closure for Win10 NetEase accessibility, KuGou marquee identity, session duration downgrade prevention, and cache self-heal.
