from __future__ import annotations
import ast
import re
import sys
from pathlib import Path
from types import SimpleNamespace

if len(sys.argv) != 2:
    print('usage: CHECK_CLOCK_SEEK_EVIDENCE_H25_REPLAY.py <main.py>')
    raise SystemExit(2)

main = Path(sys.argv[1]).resolve()
source = main.read_text(encoding='utf-8')
tree = ast.parse(source, filename=str(main))
funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
class_methods = {}
for node in tree.body:
    if isinstance(node, ast.ClassDef):
        class_methods[node.name] = {n.name: n for n in node.body if isinstance(n, ast.FunctionDef)}
fail = []

for token in (
    'CLOCK SEEK EVIDENCE CLOSURE H25',
    'H25网易云Win32视觉时钟已锁定',
    'H25网易云Win32视觉Seek确认',
    'H25网易云Win10安全交互取证',
    'H25网易云原生日志时钟未就绪',
    'H25网易云时长就绪保持无UIA安全模式',
    'H25酷狗手动歌词会话偏好已记录',
    'H25酷狗自动歌词覆盖手动会话偏好已拒绝',
    'H25酷狗Seek期间同曲Transport零点接管否决',
    'player-duration-corroborated-auto-result',
):
    if token not in source:
        fail.append('missing H25 token: ' + token)

# KuGou window-title enrichment must use the same credibility gate as ordinary Host identity.
for name in ('_start_auto_search_job', '_manual_fetch_identity_worker'):
    node = (class_methods.get('ControlPanel') or {}).get(name)
    if node is None:
        fail.append('missing core identity worker: ' + name)
        continue
    body = ast.get_source_segment(source, node) or ''
    if 'self._kugou_window_probe_identity_credible(wsong, wart)' not in body:
        fail.append(name + ' bypasses KuGou marquee/shell credibility gate')

# Provider/cache duration must never be able to certify itself. Only independent player
# duration may create/update the H24 verified row.
required = ('_h24_artist_alias_ok', '_h24_kugou_duration_row', '_h24_kugou_duration_tol', '_h24_remember_kugou_duration')
ns = {
    'time': __import__('time'),
    '_clean_name': lambda v: re.sub(r'\W+', '', str(v or '')).lower(),
    '_artist_alias_match': lambda a,b: (True, 'stub'),
    '_artist_alias_keys': lambda a: set(re.split(r'[/、,&，\s]+', str(a or ''))),
    'H24_KUGOU_DURATION_TOLERANCE_RATIO': 0.025,
    'H24_KUGOU_DURATION_TOLERANCE_MIN_MS': 3500,
}
try:
    for name in required:
        node = funcs.get(name)
        if node is None:
            fail.append('missing duration helper: ' + name)
        else:
            exec(ast.get_source_segment(source, node), ns, ns)
    remember = ns.get('_h24_remember_kugou_duration')
    rowfn = ns.get('_h24_kugou_duration_row')
    if remember and rowfn:
        fake = SimpleNamespace(_h24_kugou_verified_durations={})
        if remember(fake, '少女A', '鏡音リン', 81000, player_duration=0, source='accepted-auto-result'):
            fail.append('accepted auto result still self-certifies 81000ms')
        if rowfn(fake, '少女A', '鏡音リン'):
            fail.append('provider-only duration created a verified row')
        if not remember(fake, '少女A', '鏡音リン', 221000, player_duration=221000, source='player-proof'):
            fail.append('independent 221000ms player proof was not accepted')
        if remember(fake, '少女A', '鏡音リン', 81000, player_duration=0, source='stale-cache'):
            fail.append('stale 81000ms cache replaced player-proved 221000ms')
except Exception as exc:
    fail.append('duration evidence replay raised: ' + repr(exc))

# A committed KuGou seek, not a broad mouse-down candidate, must veto an ambiguous
# same-identity transport zero-reset for only a short post-seek window.
try:
    node = funcs.get('_h25_kugou_recent_committed_seek')
    req_node = funcs.get('_h25_request_kugou_transport_instance_from_edge')
    if node is None or req_node is None:
        fail.append('missing H25 KuGou committed-seek transport guard')
    else:
        kns = {'time': __import__('time')}
        exec(ast.get_source_segment(source, node), kns, kns)
        check = kns['_h25_kugou_recent_committed_seek']
        now = __import__('time').monotonic() * 1000.0
        fake = SimpleNamespace(
            _kugou_last_gesture_mono=now-300.0, _kugou_rail_master_active=True,
            _kugou_rail_master_absolute=True, _kugou_rail_master_reason='user-rail-gesture',
            _kugou_rail_master_track_key='song|artist', _track_key='song|artist',
            _kugou_rail_master_player_epoch=4, _media_player_epoch=4,
            _kugou_rail_master_identity_epoch=7, _track_identity_epoch=7,
        )
        if not check(fake, now):
            fail.append('recent committed KuGou seek did not arm transport-zero veto')
        fake._kugou_last_gesture_mono = now-2500.0
        if check(fake, now):
            fail.append('stale KuGou seek incorrectly vetoes later duplicate transport')
        fake._kugou_last_gesture_mono = now-300.0
        fake._kugou_rail_master_reason = 'transport-edge-local'
        if check(fake, now):
            fail.append('non-gesture KuGou rail state incorrectly arms seek veto')
        body = ast.get_source_segment(source, req_node) or ''
        for token in ('_h25_kugou_recent_committed_seek(self)', '_kugou_transport_edge_consumed_serial', 'local-zero=skip'):
            if token not in body:
                fail.append('KuGou transport request guard missing token: ' + token)
except Exception as exc:
    fail.append('KuGou committed-seek guard replay raised: ' + repr(exc))

# Visual clock proof is deliberately pure/replayable: three coherent samples spanning >720ms
# may lock, while a huge non-wallclock animation jump must restart proof.
try:
    names = ('_h25_netease_visual_proof_step',)
    vns = {
        'H25_NETEASE_VISUAL_MIN_HITS': 3,
        'H25_NETEASE_VISUAL_MIN_SPAN_MS': 720.0,
    }
    for name in names:
        node = funcs.get(name)
        if node is None:
            fail.append('missing visual proof helper: ' + name)
        else:
            exec(ast.get_source_segment(source, node), vns, vns)
    step = vns.get('_h25_netease_visual_proof_step')
    if step:
        p = None
        p, ok1 = step(p, 10000, 1000, 100, 900, 600, 221500)
        p, ok2 = step(p, 10420, 1420, 100, 900, 600, 221500)
        p, ok3 = step(p, 10840, 1840, 100, 900, 600, 221500)
        if ok1 or ok2 or not ok3:
            fail.append('coherent NetEase visual rail did not require/achieve 3-hit proof')
        q = None
        q, _ = step(q, 10000, 1000, 100, 900, 600, 221500)
        q, bad = step(q, 50000, 1420, 100, 900, 600, 221500)
        if bad or int((q or {}).get('hits') or 0) != 1:
            fail.append('non-wallclock visual jump was not rejected/reset')
except Exception as exc:
    fail.append('visual proof replay raised: ' + repr(exc))

# Win10-safe clock implementation must stay outside Chromium accessibility stacks.
for name in ('_h25_netease_capture_visual_strip', '_h25_poll_netease_safe_visual_clock', '_h25_netease_apply_verified_page_interaction'):
    node = funcs.get(name)
    if node is None:
        fail.append('missing H25 safe clock function: ' + name)
        continue
    body = ast.get_source_segment(source, node) or ''
    for forbidden in ('pywinauto', 'comtypes'):
        if forbidden in body:
            fail.append(f'{name} references forbidden in-process accessibility dependency: {forbidden}')

inter = ast.get_source_segment(source, funcs.get('_h25_netease_apply_verified_page_interaction')) if funcs.get('_h25_netease_apply_verified_page_interaction') else ''
if inter:
    if '_uia_reader.request_urgent_scan' in inter or '_uia_reader.request_interaction_point_scan' in inter:
        fail.append('H25 safe interaction still calls UIA scan APIs')
    for token in ('seek-intent', 'learned-rail-seed', 'uia-request=0', 'visual-reconfirm=1',
                  "seed_status = 'paused' if current_status == 'paused' else 'playing'"):
        if token not in inter:
            fail.append('safe interaction missing token: ' + token)

poll = ast.get_source_segment(source, funcs.get('_h25_poll_netease_safe_visual_clock')) if funcs.get('_h25_poll_netease_safe_visual_clock') else ''
if poll:
    for token in ('duration <= 5000.0', '_kugou_visual_motion_candidate', '_kugou_visual_infer_bounds', 'ncm-win32-visual-rail'):
        if token not in poll:
            fail.append('safe visual clock missing behavior token: ' + token)


# Field clicks in the Win10 VM clustered around the top of the transport band (~0.80 of
# the client height). The capture strip must include that boundary instead of starting below it.
try:
    m = re.search(r'H25_NETEASE_VISUAL_CAPTURE_Y_MIN\s*=\s*([0-9.]+)', source)
    if not m or float(m.group(1)) > 0.795:
        fail.append('NetEase safe visual capture starts below the transport-band top')
except Exception as exc:
    fail.append('NetEase capture-band replay raised: ' + repr(exc))

# Worker must use safe visual only after Bridge/native/strict-GSMTC fallback are unavailable.
for token in (
    "not fallback_trusted",
    "h25_safe_ui = self._h25_poll_netease_safe_visual_clock(status)",
    "position_source = str(h25_safe_ui.get('source') or 'ncm-win32-visual-rail')",
    "str(position_source or '').startswith('ncm-win32-')",
):
    if token not in source:
        fail.append('NetEase worker integration missing: ' + token)

# Manual KuGou payload preference is session-instance scoped and automatic results cannot
# overwrite it without independent player duration proving the new version.
for name, tokens in {
    '_h25_manual_apply': ('track_key', 'identity_epoch', 'player_epoch', 'verified-duration=0'),
    '_h25_auto_result': ('same_instance', 'player_supports_incoming', 'keep-manual-session-payload'),
}.items():
    node = funcs.get(name)
    if node is None:
        fail.append('missing H25 KuGou session wrapper: ' + name)
        continue
    body = ast.get_source_segment(source, node) or ''
    for token in tokens:
        if token not in body:
            fail.append(f'{name} missing token: {token}')

# H25 must be the final compatibility closure before the historical H14 replay-extracted block.
h25_i = source.find('# H25 clock / seek / evidence closure')
h14_i = source.find('# H14 auto-precision deadline / bounded enhancement')
if h25_i < 0 or h14_i < 0 or h25_i >= h14_i:
    fail.append('H25 block must remain before H14 replay-extracted block')

if fail:
    print('CLOCK SEEK EVIDENCE H25 REPLAY: FAIL')
    for item in fail:
        print(' -', item)
    raise SystemExit(1)

print('CLOCK SEEK EVIDENCE H25 REPLAY: PASS')
print(' - KuGou provider/cache duration cannot self-certify as verified player duration')
print(' - KuGou manual/auto title enrichment passes the marquee/shell credibility gate')
print(' - manual KuGou payload preference blocks same-instance automatic duration downgrade')
print(' - a committed KuGou rail seek vetoes only the short ambiguous same-identity local-zero edge')
print(' - Win10 frozen NetEase keeps UIA/MSAA closed and uses multi-sample Win32/GDI screen rail proof')
print(' - learned NetEase rail clicks seed seek locally and require visual reconfirmation')
print(' - absent safe evidence stays unknown instead of manufacturing a hard 0ms position')
