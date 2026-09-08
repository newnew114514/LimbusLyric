# H12 REVIEW ADDENDUM — 2026-08-26

H12 changes are presentation/control-panel only. Treat the H11 player-authority contracts below as unchanged. Any review of H12 must include `CHECK_UX_EXTENSIONS_H12_REPLAY.py` and the complete 70-gate canonical suite.

------------------------------------------------------------------------

# Review contract

## QQ authority
Software-2 remains the stable-state QQ UIA authority baseline. The following must remain source-locked to software two unless new same-machine evidence explicitly justifies a replacement:
- `MediaSessionSync._merge_uia_position`
- `MediaSessionSync._qq_phase_edge_correction`
- `MediaSessionSync._qq_select_public_clock`
- the complete `QQMusicUiAdapter` class

Rail geometry proves user interaction only. It must not directly drive provisional or formal lyric time. `QQ_RAIL_VISUAL_DIRECT` remains default 0.

## Reviewed QQ deviations
The reviewed deviations around the software-2 core are limited to:
1. QRC PC GET/POST request racing; decode/phase semantics unchanged.
2. Accessibility wake retry, urgent observation, QQ soft track reset and track epoch.
3. Stale live-control recovery after a real seek, including the 11.2s evidence window.
4. False non-rail click filtering already documented by the accuracy branch.
5. Final GSMTC/UIA identity arbitration:
   - GSMTC must be source-affine/trusted and its timeline duration must tightly match the loaded lyric duration.
   - Only then may it quarantine a contradictory UIA duration / `qq-track-switch-hint`.
   - Cached hints are quarantined too; COM wrapper invalidation remains on the UIA worker thread.
   - large GSMTC position jumps require a second advancing sample before seek authority resumes.
   - a true track switch changes GSMTC duration and releases the old-track guard immediately.

Do not reintroduce startup calibration, global one-sample QQ locks, rail-geometry lyric clocks, renderer-only geometry previews, phase-convergence experiments, or unqualified GSMTC assumptions.

## Protected behavior
- QQMusicUiAdapter old-working/software-2 class lock must pass.
- KuGou 21-method golden baseline must pass.
- Legacy unchanged-function audit must pass; reviewed QQ deviations are source-hash locked separately.
- NetEase Native / BetterNCM behavior and packaging/logging improvements remain protected.
- One-click packaging must clean project Python cache artifacts before release invariant auditing without deleting build venv/dist/work folders.

Run every installer `CHECK_*.py` gate, regenerate `SHA256_FILES.txt`, verify no project `__pycache__`/`.pyc`, and test the final ZIP before release.

## 2026-08-16 DUAL-CLOCK + CROSS-SOURCE addendum
- Keep `MediaSessionSync._merge_uia_position`, `_qq_select_public_clock`, `_qq_phase_edge_correction`, and the whole `QQMusicUiAdapter` source-identical to their locked software-2/old-working baselines. `ControlPanel._on_auto_lyric_result` has a reviewed wording-only RC UI hygiene diff and is re-locked by `CHECK_RC11_TARGETED_FIXES.py`; do not treat that wording change as authority logic.
- `MediaSessionSync._qq_direct_gsmtc_witness` is the only independent QQ GSMTC witness. Never derive its evidence from `_est_position_ms`, because the locked UIA merge intentionally rewrites that shared estimator.
- Direct GSMTC seek authority requires current-track duration identity plus a two-sample raw discontinuity proof. Host raw=0/default timestamp must leave it dormant.
- Recent-rail stale-flow protection remains for host QQ, but a confirmed independent GSMTC restart/seek may explicitly retire that stale rail state.
- Full-lyric cross-provider borrowing may change lyric content source, never player transport identity. Geometry remains non-authoritative.

## 2026-08-16 cross-source duration race addendum
- On a QQ track identity change, never treat a generic pre-bind `qq-time-pair-candidate`/`qq-time-pair-validated` duration as new-song identity; title updates can precede the compact Text pair.
- `qq-track-switch-hint` remains eligible as immediate pre-bind new-track duration evidence because it explicitly represents a duration change against the old bound track.
- Otherwise resolve duration only after the provisional bind has advanced the QQ track epoch, then keep the existing strict cross-provider duration checks unchanged.
- `installer/CHECK_QQ_CROSSSOURCE_DURATION_RACE_REPLAY.py` is a release gate for this invariant.

## 2026-08-16 fast provisional anchor addendum
- Host latency optimization is allowed only in the temporary QQ renderer lane; formal software-2 clock/seek authority remains source-locked.
- Before a QQ provisional display seed exists, do not expose candidate-detection age as a fabricated playback position/0s clock.
- A fast seed requires a bound lyric duration plus `qq-time-pair-validated`, sufficient confidence, and matching current/total duration. Wrong-duration samples must fail closed.
- The seed is display-only: never write it into `_uia_position_ms`, `_est_position_ms`, seek state, or GSMTC/UIA authority.
- Paused manual first-bind seeding additionally requires the pointer off the QQ rail; playing auto-track may provisionally seed while the pointer rests on the rail, because formal hover/advancing proof still gates committed authority.
- `installer/CHECK_QQ_FAST_PROVISIONAL_ANCHOR_REPLAY.py` is a release gate.

## 2026-08-16 KuGou causal-clock guard contract addendum

- `CHECK_KUGOU_GOLDEN_BASELINE.py` remains authoritative: all 21 locked KuGou methods must stay source-identical.
- The only approved KuGou change in this build is the outer Async publication guard plus worker routing into it.
- `continuous-no-wrap` by itself may no longer become public lyric-time authority; it remains valid internal discovery evidence only.
- Causal public trust requires seek-target response or pause-freeze response. A candidate that advances materially while transport is paused must be rejected and its matching persisted seed cleared.
- Do not solve this by shortening the golden proof window, changing KRC matching, or adding geometry time authority.

### 2026-08-16 KuGou postscan baseline follow-up
- Host log 15:45 reproduced a broad-scan timestamp inflation: 42 moving pause/resume candidates were found, then all rejected because scan-start time was used as C sample time.
- `_try_kugou_pause_resume_causal_clock` now timestamps C/D per memory block and E per address.
- `_kugou_pause_resume_match_candidate(..., resume_head_prevalidated=True)` is used only after C already passed the pause-freeze + resume-window gate.
- Do not convert this into a shorter motion-only proof. KuGou's 21 golden methods remain source-identical.
## 2026-08-16 RC release-hardening addendum
- User config schema is `5`. Runtime `ALL` is first-class again and coexists with independent `qq` / `netease` / `kugou` / `spotify` slots. Migration must preserve both sides when present; schema-v4 rows with only provider slots remain `per_player` by default. Retired frontend/simple/loop keys and hidden legacy pacing keys may still be removed while perspective, sync offsets, presets, song styles and player profiles are preserved.
- Perspective X/Y/horizontal compensation remain public visual preferences. The reset action is perspective-only and must not touch transport/timing state.
- Unified diagnostics root remains `%LOCALAPPDATA%\LimbusLyric\logs`; keep at most the newest five sessions, with a bounded long-session tail.
- PyInstaller spec is semantically locked by `CHECK_PACKAGING_CONTRACT.py`: one-folder layout, runtime dependencies, MFC, icon and windowed EXE remain mandatory. Formatting/comments and reviewed dependency-list additions must not require a new byte hash.
- Frozen packaging smoke must validate runtime dependencies plus bundled icon/config-root/log-root basics before Inno packaging proceeds.
- `CHECK_RC_RELEASE_HARDENING_REPLAY.py` and `CHECK_PACKAGING_CONTRACT.py` are mandatory release gates.


## 2026-08-17 DIY ALL + per-player addendum
- User-requested product change supersedes the 2026-08-16 “runtime ALL retired” DIY rule only; it does not relax any QQ/NetEase/KuGou transport or timing authority lock.
- `mode=all` means one `rules["all"]` payload is active for all three supported players. `mode=per_player` means only the actual player's `qq` / `netease` / `kugou` payload is active.
- Mode switching is non-destructive: inactive payloads remain stored. Seeding is allowed only into missing slots during a mode transition and must never overwrite an existing inactive payload.
- The row-level ALL/四家独立 button and the 编辑播放器 combo are two synchronized controls for the same application mode.

## 2026-08-17 UX/script polish review boundary
- Review `CHECK_UX_SCRIPT_INSTRUMENTAL_REPLAY.py` together with the existing authority/golden gates.
- Hangul change is presentation classification only; do not invent provider timestamps or special Korean clock offsets.
- Instrumental title-card substitution must remain renderer-only and must not become lyric/provider/transport identity evidence.
- Tutorial/status/DIY-preview/font-manager changes are UI/config only.
- Slow-call telemetry may measure and log but may not alter provider return values, synchronization thresholds, or thread ownership.
- KuGou GUI path must remain free of synchronous `tasklist` subprocess enumeration.

## 2026-08-18 V29 review boundary
- Do not redesign V28 precision visual handoff; its four handoff/reveal helpers and the atlas raster builder are source-locked by the V29 gate.
- KuGou `transport_generation` is not song identity and must not trigger provider refetch, DIY reselection, or cross-player authority. Hidden inference is valid only at a known end while raw status remains playing and real Host/visual rail evidence is stale.
- Burst admission may discard only already-fading exits. It must not clear current text, readable history, shrink fonts, disable glow/outline/audio scaling, or replace random spread with a fixed layout.
- Atlas optimization may alter cache lifecycle/diagnostics only. Supersampling, glyph pixels, font styling and soft-glow raster behavior remain protected.
- Provider timeout traceback suppression applies only to expected timeout exception classes; unexpected exceptions retain the historical traceback path.
