#!/usr/bin/env python3
import ast, html, re, sys, time
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V20_TRANSACTION_IDENTITY_REPLAY.py <main.py>')
p = Path(sys.argv[1])
src = p.read_text(encoding='utf-8')
tree = ast.parse(src)

def fail(msg):
    print('LYRIC PIPELINE V20 TRANSACTION IDENTITY + BACKGROUND CLOCK HANDOFF REPLAY: FAIL')
    print('  -', msg)
    raise SystemExit(1)

def fn(cls, name):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name:
                    return item, ast.get_source_segment(src, item)
    fail(f'missing {cls}.{name}')

if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V20','INSTRUMENTAL-RUNTIME-V21','INSTRUMENTAL-RUNTIME-V22','INSTRUMENTAL-RUNTIME-V23','INSTRUMENTAL-RUNTIME-V24','INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')):
    fail('V20+ build marker missing')

# V19 root regression: an in-flight title|artist transaction must own identity too.
_, active = fn('ControlPanel', '_active_auto_target_matches')
for n in ('_auto_target_key', "split('|', 1)", '_same_track'):
    if n not in active:
        fail(f'pending-target identity helper missing: {n}')

_, kg = fn('ControlPanel', '_promote_kugou_background_identity_hint')
for n in (
    '_active_auto_target_matches', '酷狗后台同曲活动事务抖动抑制',
    'identity-reset=skip', 'network-restart=skip', 'evidence_mono_ms',
    'metadata_age=', '_request_auto_track'
):
    if n not in kg:
        fail(f'KuGou transaction guard missing: {n}')
if kg.index('_active_auto_target_matches') > kg.index('_request_auto_track'):
    fail('KuGou pending-target guard runs after transaction request')

_, monitor = fn('ControlPanel', '_monitor_track_change')
if '_active_auto_target_matches' not in monitor:
    fail('generic detector can still supersede an equivalent pending target')

_, request = fn('ControlPanel', '_request_auto_track')
if '_active_auto_target_matches' not in request:
    fail('final request-level pending-target fail-safe missing')
if request.index('_active_auto_target_matches') > request.index('self.media_sync.bind_track'):
    fail('request fail-safe runs after MediaSync reset')

# QQ background improvement may skip identity debounce only; it cannot claim clock/seek authority.
_, qq = fn('ControlPanel', '_promote_qq_background_identity_hint')
for n in (
    "currentText() or '') != 'QQ音乐'", '_active_auto_target_matches', 'evidence_mono_ms',
    'metadata_age=', 'clock-authority=unchanged', '_request_auto_track'
):
    if n not in qq:
        fail(f'QQ background identity helper missing: {n}')
for forbidden in ('seek_to(', '_qq_queue_seek(', 'media_sync.bind_track('):
    if forbidden in qq:
        fail(f'QQ metadata helper polluted playback authority: {forbidden}')

_, front = fn('ControlPanel', '_refresh_frontend_status')
for n in (
    "player_name == 'QQ音乐'", 'qq-gsmtc-title-change', 'media_metadata_mono',
    'age_ms <= 1500.0', "_source_matches_process_hint(media_source, 'qqmusic.exe')",
    '_promote_qq_background_identity_hint', 'kugou-gsmtc-title-change'
):
    if n not in front:
        fail(f'fresh process-affine background route missing: {n}')

# Existing strong absolute-clock behavior is unchanged; V20 only adds explicit evidence in logs.
_, handoff = fn('MediaSessionSync', '_guard_auto_local_handoff')
for n in ('qq-time-pair-validated', '后台临时时钟可信绝对锚硬交接', 'presentation-snap=1', 'seek=unchanged'):
    if n not in handoff:
        fail(f'trusted absolute handoff diagnostic missing: {n}')
if 'if strong or abs_drift <= 6500.0' not in handoff:
    fail('historical strong-clock immediate handoff rule changed/removed')

# Dynamic regression harness compiled from only the small source methods: no PyQt import needed.
helpers = {
    n.name: n for n in tree.body
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    and n.name in {'_clean_name', '_artist_alias_keys', '_artist_alias_match'}
}
cp = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ControlPanel')
want = {
    '_same_track', '_track_identity', '_active_auto_target_matches',
    '_promote_kugou_background_identity_hint', '_promote_qq_background_identity_hint'
}
methods = [n for n in cp.body if isinstance(n, ast.FunctionDef) and n.name in want]
mini = ast.Module(
    body=[*helpers.values(), ast.ClassDef(name='ControlPanel', bases=[], keywords=[], body=methods, decorator_list=[])],
    type_ignores=[]
)
ast.fix_missing_locations(mini)
ns = {
    're': re, 'html': html, 'time': time, 'EVIDENCE_CLOCK_ENABLED': True,
    'write_error_log': lambda *a, **k: None,
}
exec(compile(mini, '<v20-mini>', 'exec'), ns)
CP = ns['ControlPanel']

class Check:
    def isChecked(self): return True
class KGCombo:
    def currentText(self): return '酷狗音乐'
class QQCombo:
    def currentText(self): return 'QQ音乐'

kg_obj = CP()
kg_obj.player_combo = KGCombo(); kg_obj.auto_track_check = Check()
kg_obj._is_started = True; kg_obj._auto_armed = True
kg_obj._loaded_song = 'Hop'; kg_obj._loaded_artist = 'Azis'
kg_obj._note_auto_transport_hint = lambda *a, **k: None
kg_calls = []
kg_obj._request_auto_track = lambda *a, **k: kg_calls.append(a)

# Exact V19 failure in both directions: title|full <-> title|blank must never restart.
kg_obj._auto_target_key = '但|草东没有派对'
if not kg_obj._active_auto_target_matches('但', ''):
    fail('full pending target does not match blank-artist update')
if kg_obj._promote_kugou_background_identity_hint('但', '', source='kugou-gsmtc-title-change'):
    fail('blank-artist KuGou update restarted full-artist pending transaction')
kg_obj._auto_target_key = '但|'
if not kg_obj._active_auto_target_matches('但', '草东没有派对'):
    fail('blank pending target does not match full-artist update')
if kg_obj._promote_kugou_background_identity_hint('但', '草东没有派对', source='kugou-window-title-probe'):
    fail('full-artist KuGou update restarted blank-artist pending transaction')
if kg_calls:
    fail(f'KuGou equivalent pending identity caused network restart: {kg_calls!r}')

# A genuinely different KuGou song still commits once, seeded from fresh evidence age.
kg_obj._auto_target_key = ''
if not kg_obj._promote_kugou_background_identity_hint(
    '山海', '草东没有派对', source='kugou-gsmtc-title-change',
    evidence_mono_ms=time.monotonic() * 1000.0 - 350.0
):
    fail('genuine KuGou new song was not promoted')
if kg_calls != [('山海', '草东没有派对')]:
    fail(f'genuine KuGou new song did not commit exactly once: {kg_calls!r}')
kg_age = (time.monotonic() - kg_obj._auto_candidate_since) * 1000.0
if not 250.0 <= kg_age <= 650.0:
    fail(f'KuGou metadata age not preserved into provisional display clock: {kg_age:.1f}ms')

qq_obj = CP()
qq_obj.player_combo = QQCombo(); qq_obj.auto_track_check = Check()
qq_obj._is_started = True; qq_obj._auto_armed = True
qq_obj._loaded_song = '旧歌'; qq_obj._loaded_artist = '甲'; qq_obj._auto_target_key = ''
qq_obj._note_auto_transport_hint = lambda *a, **k: None
qq_calls = []
qq_obj._request_auto_track = lambda *a, **k: qq_calls.append(a)
if not qq_obj._promote_qq_background_identity_hint(
    '新歌', '乙', source='qq-gsmtc-title-change',
    evidence_mono_ms=time.monotonic() * 1000.0 - 420.0
):
    fail('fresh process-affine QQ metadata did not promote new identity')
if qq_calls != [('新歌', '乙')]:
    fail(f'QQ metadata promotion did not commit exactly once: {qq_calls!r}')
qq_age = (time.monotonic() - qq_obj._auto_candidate_since) * 1000.0
if not 300.0 <= qq_age <= 700.0:
    fail(f'QQ metadata age not preserved into provisional display clock: {qq_age:.1f}ms')

print('LYRIC PIPELINE V20 TRANSACTION IDENTITY + BACKGROUND CLOCK HANDOFF REPLAY: PASS')
print('  KuGou title|blank/full pending identity oscillation blocked in both directions: PASS')
print('  final auto-track request cannot reset an equivalent in-flight transaction: PASS')
print('  fresh KuGou/QQ process-affine metadata skips software debounce only: PASS')
print('  trusted absolute clock handoff remains immediate; no fake catch-up/seek added: PASS')
