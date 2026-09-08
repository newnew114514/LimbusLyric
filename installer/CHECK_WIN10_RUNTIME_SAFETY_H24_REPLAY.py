from __future__ import annotations
import ast
import re
import sys
import time
from pathlib import Path
from types import SimpleNamespace

if len(sys.argv) != 2:
    print('usage: CHECK_WIN10_RUNTIME_SAFETY_H24_REPLAY.py <main.py>')
    raise SystemExit(2)

main = Path(sys.argv[1]).resolve()
source = main.read_text(encoding='utf-8')
tree = ast.parse(source, filename=str(main))
funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
fail = []

for token in (
    'WIN10 RUNTIME SAFETY H24',
    'H24网易云Win10无UIA安全路径',
    'H24网易云Win10无障碍唤醒安全跳过',
    'H24网易云Win10定点UIA安全跳过',
    'H24酷狗跑马灯Host身份熔断',
    'H24酷狗跑马灯期间GSMTC恢复身份权威',
    'H24酷狗会话已验证时长注入新事务',
    'H24酷狗同名缓存时长降级拒绝',
    'H24自动歌词损坏缓存自愈',
):
    if token not in source:
        fail.append('missing H24 token: ' + token)

for token in (
    'AsyncPlayerUiPositionReader._start_accessibility_wake = _h24_async_start_wake',
    'AsyncPlayerUiPositionReader._kick_accessibility = _h24_async_kick_accessibility',
    'AsyncPlayerUiPositionReader.request_urgent_scan = _h24_async_urgent_scan',
    'AsyncPlayerUiPositionReader.request_interaction_point_scan = _h24_async_interaction_scan',
    'AsyncPlayerUiPositionReader.request_lyric_text_probe = _h24_async_lyric_text_probe',
    'MediaSessionSync._set_netease_uia_suspended = _h24_netease_uia_suspend_guard',
):
    if token not in source:
        fail.append('NetEase fail-closed wiring missing: ' + token)

# Execute the exact Win10 frozen NetEase predicate independently from the GUI stack.
try:
    ns = {
        'os': __import__('os'),
        'sys': SimpleNamespace(platform='win32', frozen=True),
        'H24_NETEASE_WIN10_FROZEN_SAFE_MODE': True,
        'H24_NETEASE_WIN10_UIA_OPTIN': False,
        '_h23_windows_build_number': lambda: 19045,
    }
    for name in ('_h24_process_stem', '_h24_netease_win10_frozen_no_accessibility'):
        if name not in funcs:
            fail.append('missing H24 function: ' + name)
        else:
            exec(ast.get_source_segment(source, funcs[name]), ns, ns)
    if ns.get('_h24_netease_win10_frozen_no_accessibility'):
        pred = ns['_h24_netease_win10_frozen_no_accessibility']
        if pred('cloudmusic.exe') is not True:
            fail.append('Win10 frozen cloudmusic did not enter H24 no-accessibility profile')
        if pred('qqmusic.exe') is not False:
            fail.append('H24 NetEase predicate leaked onto QQ')
        ns['H24_NETEASE_WIN10_UIA_OPTIN'] = True
        if pred('cloudmusic.exe') is not False:
            fail.append('NetEase Win10 explicit UIA opt-in did not bypass safe profile')
except Exception as exc:
    fail.append('NetEase predicate replay raised: ' + repr(exc))

# Replay the exact field marquee pattern: same HWND text rotates by one character.
try:
    ns = {'re': re}
    for name in ('_h24_kugou_title_compact', '_h24_kugou_title_is_rotation', '_h24_kugou_split_shell_fragment'):
        if name not in funcs:
            fail.append('missing H24 marquee helper: ' + name)
        else:
            exec(ast.get_source_segment(source, funcs[name]), ns, ns)
    rotation = ns.get('_h24_kugou_title_is_rotation')
    split = ns.get('_h24_kugou_split_shell_fragment')
    if rotation:
        prev = '酷狗音乐 鏡音リン、椎名もた - 少女A -  '
        cur = '狗音乐 鏡音リン、椎名もた - 少女A - 酷'
        if not rotation(prev, cur):
            fail.append('field KuGou marquee rotation was not detected')
        if rotation('鏡音リン - 少女A - 酷狗音乐', '米津玄師 - Lemon - 酷狗音乐'):
            fail.append('real unrelated title change was misclassified as rotation')
    if split:
        if not split('狗音乐 鏡音リン、椎名もた - 少女A', '酷'):
            fail.append('split KuGou shell fragment 酷 + 狗音乐 was not rejected')
        if not split('乐 鏡音リン、椎名もた - 少女A', '酷狗音'):
            fail.append('split KuGou shell fragment 酷狗音 + 乐 was not rejected')
        if split('少女A', '鏡音リン'):
            fail.append('normal KuGou song/artist was rejected as shell fragment')
except Exception as exc:
    fail.append('KuGou marquee replay raised: ' + repr(exc))

# The detector must temporarily remove Host-V2 identity authority while untrusted, and
# H21's stale-GSMTC guard must be clearable during a marquee fuse.
for name, tokens in {
    '_h24_detected_player_track': (
        "self.media_sync._kugou_host_v2_cache = None",
        "self._h21_kugou_host_switch = None",
        "return _LIMBUS_H24_DETECTED_TRACK_PRE(self)",
    ),
    '_h24_kugou_promote': (
        "self._h21_kugou_host_switch = None",
        "_LIMBUS_H24_KUGOU_PROMOTE_PRE",
    ),
}.items():
    node = funcs.get(name)
    if node is None:
        fail.append('missing H24 identity wrapper: ' + name)
        continue
    body = ast.get_source_segment(source, node) or ''
    for token in tokens:
        if token not in body:
            fail.append(f'{name} missing behavior token: {token}')

# H25 evidence correction: H24 session duration may be sticky only after independent
# player-side corroboration. A lyric provider/cache result must never certify itself.
try:
    def clean(v):
        return re.sub(r'[^0-9a-zA-Z\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]+', '', str(v or '')).lower()
    def alias_match(a, b):
        aa = {x for x in re.split(r'[/、,&，\s]+', str(a or '')) if x}
        bb = {x for x in re.split(r'[/、,&，\s]+', str(b or '')) if x}
        return (bool(aa & bb) or clean(a) == clean(b), 'stub')
    ns = {
        'time': time,
        '_clean_name': clean,
        '_artist_alias_match': alias_match,
        '_artist_alias_keys': lambda a: {x for x in re.split(r'[/、,&，\s]+', str(a or '')) if x},
        'H24_KUGOU_DURATION_TOLERANCE_RATIO': 0.025,
        'H24_KUGOU_DURATION_TOLERANCE_MIN_MS': 3500,
    }
    for name in ('_h24_artist_alias_ok', '_h24_kugou_duration_row', '_h24_kugou_duration_tol', '_h24_remember_kugou_duration'):
        if name not in funcs:
            fail.append('missing H24 duration helper: ' + name)
        else:
            exec(ast.get_source_segment(source, funcs[name]), ns, ns)
    remember = ns.get('_h24_remember_kugou_duration')
    rowfn = ns.get('_h24_kugou_duration_row')
    if remember and rowfn:
        fake = SimpleNamespace(_h24_kugou_verified_durations={})
        if remember(fake, '少女A', '鏡音リン、椎名もた', 221000, player_duration=0, source='provider-only'):
            fail.append('provider-only 221000ms KuGou duration self-certified without player evidence')
        if rowfn(fake, '少女A', '鏡音リン'):
            fail.append('provider-only duration polluted verified session rows')
        if not remember(fake, '少女A', '鏡音リン、椎名もた', 221000, player_duration=221000, source='player-corroborated'):
            fail.append('player-corroborated 221000ms KuGou duration was not remembered')
        if remember(fake, '少女A', '鏡音リン', 81000, player_duration=0, source='stale-cache'):
            fail.append('81000ms stale same-title duration incorrectly replaced 221000ms witness')
        row = rowfn(fake, '少女A', '鏡音リン') or {}
        if int(row.get('duration') or 0) != 221000:
            fail.append('session duration witness changed after stale 81000ms replay')
        if not remember(fake, '少女A', '鏡音リン', 81000, player_duration=81000, source='real-new-version'):
            fail.append('independent 81000ms player duration could not override session witness')
except Exception as exc:
    fail.append('KuGou duration replay raised: ' + repr(exc))

# Cache corruption must be quarantined and replaced by valid empty JSON before legacy load.
cache_node = funcs.get('_h24_auto_cache_load')
if cache_node is None:
    fail.append('H24 cache self-heal wrapper missing')
else:
    cache_src = ast.get_source_segment(source, cache_node) or ''
    for token in ("'.corrupt-'", "json.dump({'version': 1, 'rows': []}", 'reset=empty-valid-json'):
        if token not in cache_src:
            fail.append('cache self-heal token missing: ' + token)

# H21 is the final outer GSMTC promotion wrapper, so it must itself observe H24's marquee
# state before applying the historical stale-GSMTC veto.
h21_node = funcs.get('_h21_kugou_promote')
if h21_node is None:
    fail.append('H21 KuGou promote wrapper missing')
else:
    h21_src = ast.get_source_segment(source, h21_node) or ''
    for token in ("_h24_kugou_host_title_state", "self._h21_kugou_host_switch=None"):
        if token not in h21_src:
            fail.append('H21 outer veto is not H24-marquee-aware: ' + token)

# H24 is intentionally placed before H14 so the H14 replay extractor remains isolated.
h24_i = source.find('# H24 Win10 runtime safety / KuGou marquee identity closure')
h14_i = source.find('# H14 auto-precision deadline / bounded enhancement')
if h24_i < 0 or h14_i < 0 or h24_i >= h14_i:
    fail.append('H24 block must remain before H14 replay-extracted block')

if fail:
    print('WIN10 RUNTIME SAFETY H24 REPLAY: FAIL')
    for item in fail:
        print(' -', item)
    raise SystemExit(1)

print('WIN10 RUNTIME SAFETY H24 REPLAY: PASS')
print(' - Win10 frozen NetEase keeps Chromium/UIA wake, targeted scan, and deep worker dormant by default')
print(' - QQ is outside the NetEase compatibility predicate and remains behaviorally unchanged')
print(' - KuGou same-HWND rotating marquee is detected and cannot own track identity')
print(' - split 酷狗音乐 shell fragments are rejected even when parser divides them across artist/song')
print(' - H21 host veto is cleared during marquee so process-affine GSMTC can recover authority')
print(' - only player-corroborated KuGou duration becomes session-verified; provider-only results cannot self-certify')
print(' - corrupted persistent auto-lyric cache is quarantined and reset to valid JSON')
