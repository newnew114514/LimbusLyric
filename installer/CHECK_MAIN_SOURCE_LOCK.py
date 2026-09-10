# 2026-09-09 R9.2: QQ modern musicu desktop search primary with legacy standby; trusted NetEase song-ID cover direct fetch; clock/seek/render/identity validators unchanged.
# 2026-09-09 Visual Continuity + Frame Budget R9: retire R8 false performance fuse/history freeze, preserve H51 per-line size cache across same-track precise upgrades, and bound variable-size visible prewarm; mature entrance/hold/exit/material effects restored for all players.
# 2026-09-09 Variable Font Stability + Shared Frame Pacing R8: reviewed shared LyricWindow/FadingLine variable-size row-material policy, held-row geometry freeze, secondary history cadence, and user-facing copy cleanup; all player/provider clock/search/seek ownership unchanged.
# 2026-09-09 Switch Latency + Recording Stability R7: reviewed bounded fast ordinary-provider race plus switch-time Atlas/speculative admission quiet; player identity/version/clock/seek and precise verification contracts unchanged.
# 2026-09-09 Feedback Panel R6.1: local copy-first feedback workflow; mailto retained only as optional convenience; playback/render/search contracts unchanged.
# 2026-09-09 Release Last Mile R6: reviewed QQ post-bind duration-self-proof rescue and late-GUI speculative/OBS mirror backpressure; mature player/search/clock/seek/render formulas unchanged.
# 2026-09-08 R2.5 release closure: robust KuGou transport replay, NetEase ID-cache replay isolation, and stable per-line random font sizing; protected player authority unchanged.
# 2026-09-08 Render Resilience R2.5: reviewed held-history compiled fragment geometry, custom-font coverage LRU/invalidation, and style-scoped song-atlas fuse; player/search/clock/frontend wrapper topology unchanged.
# 2026-09-08 Visibility Clock Safety R2.4: reviewed cross-player first-attach lifecycle ownership, startup-existing no-synthetic-zero invariant, renderer-row visibility commit, and capability-scoped async clock rescue; historical frontend wrapper chains unchanged.
# 2026-09-08 Runtime UX + Core R2.3.3: field-log hotfix for missing QPalette paint dependency in region previews; no player/renderer/UI-layout authority changes.
# 2026-09-08 Runtime UX + Core R2.3.2: audited preview frame/state ownership, physically retired empty preset card, and staged-vs-active core contracts; no player/renderer authority changes.
# 2026-09-08 Runtime UX + Core R2.3.1: reviewed H78-safe title preview attachment; no player/renderer semantics changed.
# 2026-09-08 Runtime UX + Core R2.3: reviewed title-adjacent compact sticky preview, inline region map, frequent-first subtitle hierarchy, sampledAt/capability contract, and unified render hints; historical frontend wrapper chains preserved.
# 2026-09-08 Runtime Polish R2.2.1: compact page-local preview restoration; no runtime/player/renderer semantics changed.
# 2026-09-08 Runtime Polish R2.2: reviewed KuGou wall-clock visual proof, primary-owned bilingual placement, row/lane-atomic cold material fallback, cover colour/backoff ownership, and Studio placement/preview UX; historical frontend wrapper chains preserved.
from pathlib import Path
import hashlib,sys
# 2026-09-08 Runtime Convergence R2.1: reviewed first-safe-main startup, transport/search identity separation, rapid-switch cancellation debounce, and KuGou transport-scoped gesture invalidation; frontend runtime installation chains unchanged.
# 2026-09-08 Runtime Fix R2: reviewed QQ advancing-time duration proof + QQ search 5xx circuit breaker + cross-provider precise-version quarantine + KuGou background holdover/visual quarantine + transport visual-epoch reset; frontend runtime installation chains unchanged.
# 2026-09-08 Stabilization Contract S2: reviewed provider/query registry + playback snapshot contract + bounded fault journal + patch-debt freeze + isolated H95 fallback/source-lock audit fixes; live player clock/seek authorities unchanged.
EXPECTED = "99d8404ef7319fb70f77b108d5d4842e4a72f05695c961eed5a415aa9485ac31"
if len(sys.argv)!=2: raise SystemExit(2)
text=Path(sys.argv[1]).read_text(encoding='utf-8')
normalized='\n'.join(text.splitlines()).rstrip()+'\n'
actual=hashlib.sha256(normalized.encode('utf-8')).hexdigest()
if actual!=EXPECTED:
    print('MAIN SOURCE LOCK: FAIL')
    print('  expected='+EXPECTED)
    print('  actual  ='+actual)
    raise SystemExit(31)
print('MAIN SOURCE LOCK: PASS '+actual)
