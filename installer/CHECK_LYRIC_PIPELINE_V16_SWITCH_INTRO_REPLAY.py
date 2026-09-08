#!/usr/bin/env python3
import ast, sys
from pathlib import Path
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V16_SWITCH_INTRO_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def fail(msg):
    print('LYRIC PIPELINE V16 SWITCH/INTRO REPLAY: FAIL'); print('  -',msg); raise SystemExit(1)
def fn(cls,name):
    for node in tree.body:
        if isinstance(node,ast.ClassDef) and node.name==cls:
            for item in node.body:
                if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)) and item.name==name:
                    return ast.get_source_segment(src,item)
    fail(f'missing {cls}.{name}')

if not any(f'INSTRUMENTAL-RUNTIME-V{i}' in src for i in range(16, 30)): fail('V16+ build marker missing')
# 1) Progressive stage must remain alive after fast result records the loaded track.
on=fn('ControlPanel','_on_auto_lyric_result')
for n in ('progressive_pending', '自动歌词快速首屏保持事务', 'self._auto_target_key = key',
          'progressive_keep_fast', '精确增强无更优结果'):
    if n not in on: fail(f'progressive transaction retention missing: {n}')
if on.index('if progressive_pending:\n            return') < on.index('自动歌词快速首屏保持事务'):
    fail('fast stage returns before preserving target transaction')
worker=fn('ControlPanel','_start_auto_search_job')
for n in ('keep_fast=False','自动歌词精确升级结束保留快速歌词','keep_fast=True','自动歌词精确升级完成'):
    if n not in worker: fail(f'precision close/upgrade contract missing: {n}')
# Silent return after the two known keep-fast outcomes was the V15 stuck-transaction bug.
for marker in ('自动歌词精确升级失败保留快速歌词','自动歌词精确升级无需替换'):
    pos=worker.index(marker)
    tail=worker[pos:pos+1200]
    if 'emit_result(' not in tail or 'keep_fast=True' not in tail:
        fail(f'{marker} still exits without closing the progressive transaction')

# 2) V16 briefly froze old visual on first different candidate. V17 intentionally
# superseded that behavior to restore immediate normal-lyric continuity, so later builds
# must not be failed for removing the obsolete pre-bind freeze. The dedicated V17 gate
# source-locks the replacement behavior.
mon=fn('ControlPanel','_monitor_track_change')
modern_display_restore = any(f'INSTRUMENTAL-RUNTIME-V{i}' in src for i in range(17, 30))
if not modern_display_restore:
    for n in ('_freeze_old_overlay_for_switch','first-different-track-candidate','_restore_track_switch_visual_hold'):
        if n not in mon: fail(f'pre-bind visual hold missing: {n}')
    freeze=fn('ControlPanel','_freeze_old_overlay_for_switch')
    for n in ('self.lyric_window.stop_lyric()','media-rebind=0','切歌候选立即冻结旧字幕'):
        if n not in freeze: fail(f'freeze helper contract missing: {n}')
    player=fn('ControlPanel','_on_player_selection_visual_change')
    if '播放器切换立即冻结旧字幕' not in player or '_freeze_old_overlay_for_switch' not in player:
        fail('player switch does not immediately freeze previous provider visual')
    init=fn('ControlPanel','__init__')
    if 'currentTextChanged.connect(self._on_player_selection_visual_change)' not in init:
        fail('player switch visual freeze is not wired')
else:
    if '_freeze_old_overlay_for_switch' in mon or 'first-different-track-candidate' in mon:
        fail('V17+ normal-display restore regressed to obsolete V16 candidate freeze')

# 3) V16 used a dedicated no-shake soft title renderer. V19 deliberately superseded
# that visual special-case so intro/title/pure-music cards inherit the user's ordinary
# entrance/shake/typewriter settings. Later builds are checked by the dedicated V19 gate.
user_effect_intro = any(f'INSTRUMENTAL-RUNTIME-V{i}' in src for i in range(19, 30))
launch=fn('ControlPanel','_launch_current_lyrics')
if not user_effect_intro:
    vis=fn('LyricWindow','_ordinary_visual_state')
    for n in ("body.lstrip().startswith('♫ ')",'INTRO_TITLE_SOFT_ENTRY_MS',"self._flow_mode = 'intro-credit-soft'",'_intro_title_entry_started_mono','time.monotonic()','alpha = 0.025'):
        if n not in vis: fail(f'title soft entry missing: {n}')
    clock=fn('LyricWindow','check_lyric_time')
    if '_intro_title_entry_started_mono' not in clock or "startswith('♫ ')" not in clock:
        fail('title fade is still based only on playback age instead of actual visual line entry')
    for n in ('纯音乐歌曲卡柔和入场','INSTRUMENTAL_CARD_HOLD_MS','片头显示状态'):
        if n not in launch: fail(f'launch intro diagnostics missing: {n}')
else:
    for n in ('INSTRUMENTAL_CARD_HOLD_MS','片头显示状态','纯音乐歌曲卡沿用用户入场效果'):
        if n not in launch: fail(f'V19+ user-effect intro contract missing: {n}')
if "_instrumental_track_card_lrc" not in launch: fail('instrumental card substitution disappeared')

# 4) Explicit provider pure-music notices are valid ordinary-tier results even without LRC timestamps.
for name, marker in (
    ('_search_qq_ordinary','QQ经典模式纯音乐占位命中'),
    ('_search_kugou_ordinary','酷狗经典模式纯音乐占位命中'),
    ('_search_netease_ordinary','网易云经典模式纯音乐占位命中')):
    body=fn('LyricSearchEngine',name)
    if '_is_instrumental_boilerplate_payload(ordinary)' not in body or marker not in body:
        fail(f'{name} does not accept explicit untimed instrumental boilerplate')
    pure=body.index('_is_instrumental_boilerplate_payload(ordinary)')
    timed=body.index("re.search(r'\\[\\d{1,3}:\\d{1,2}', ordinary)")
    if pure > timed: fail(f'{name} checks timed LRC before explicit pure-music notice')

# Provider clocks / seek cores remain outside this patch by design.
for name in ('_qq_poll_pointer_gesture','_kugou_poll_pointer_gesture','_kugou_commit_gesture_seek'):
    body=fn('MediaSessionSync',name)
    if 'INSTRUMENTAL-RUNTIME-V16' in body or '切歌候选立即冻结旧字幕' in body:
        fail(f'low-level clock/gesture method was polluted: {name}')

print('LYRIC PIPELINE V16 SWITCH/INTRO REPLAY: PASS')
print('  fast ordinary display retains its precision transaction instead of self-cancelling: PASS')
print('  V16 candidate-freeze history / V17+ normal-display supersession: PASS')
print('  V16 soft-title history / V19+ user-effect intro supersession: PASS')
print('  explicit untimed pure-music provider notices terminate at ordinary tier: PASS')
