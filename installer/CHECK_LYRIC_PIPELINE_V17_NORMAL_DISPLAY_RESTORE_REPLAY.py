#!/usr/bin/env python3
import ast, sys
from pathlib import Path
if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V17_NORMAL_DISPLAY_RESTORE_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def fail(msg):
    print('LYRIC PIPELINE V17 NORMAL DISPLAY RESTORE REPLAY: FAIL'); print('  -', msg); raise SystemExit(1)
def fn(cls,name):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for item in node.body:
                if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)) and item.name == name:
                    return ast.get_source_segment(src,item)
    fail(f'missing {cls}.{name}')

if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V17','INSTRUMENTAL-RUNTIME-V18','INSTRUMENTAL-RUNTIME-V19','INSTRUMENTAL-RUNTIME-V20','INSTRUMENTAL-RUNTIME-V21','INSTRUMENTAL-RUNTIME-V22','INSTRUMENTAL-RUNTIME-V23','INSTRUMENTAL-RUNTIME-V24','INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')): fail('V17+ build marker missing')

# 1) First metadata candidate must not blank the currently healthy lyric.
mon=fn('ControlPanel','_monitor_track_change')
segment=mon[mon.index('if key != self._auto_candidate_key:'):]
segment=segment[:segment.index('self._auto_candidate_hits += 1')]
if '_freeze_old_overlay_for_switch' in segment or 'stop_lyric()' in segment:
    fail('first different-track candidate still blanks old lyric before confirmation')
if '_request_auto_track(song, artist)' not in segment:
    fail('transport-hint fast-confirm path disappeared')
player=fn('ControlPanel','_on_player_selection_visual_change')
if '_freeze_old_overlay_for_switch' in player or 'stop_lyric' in player:
    fail('player selection still blanks lyric before confirmed track transaction')

# 2) Confirmed QQ auto-track may render ordinary lyrics from the existing display-only local lane
# while formal QQ position/duration proof is still converging.
snap=src
for n in ("seed_reason == 'auto-track'", "position_ms = self._auto_local_position(status)",
          "position_source = 'qq-auto-track-local-provisional'", 'QQ新曲首锚前临时时钟显示',
          'authority=display-only | seek=unchanged'):
    if n not in snap: fail(f'QQ provisional normal-lyric display fallback missing: {n}')
# Startup/manual attach must still wait for a real seed.
if "position_source = 'qq-auto-track-wait-display-seed'" not in snap:
    fail('startup/manual seed wait protection disappeared')

# 3) Precision result must close the duration-pending state through same-key bind_track without reset.
on=fn('ControlPanel','_on_auto_lyric_result')
for n in ('same_loaded_for_upgrade', '_complete_same_track_duration', '自动歌词精确升级热替换'):
    if n not in on: fail(f'same-track duration completion missing: {n}')
helper=fn('ControlPanel','_complete_same_track_duration')
for n in ("key != media_key", 'self.media_sync.bind_track(', '自动歌词精确升级补齐同曲时长', 'same-track=1 | media-reset=0'):
    if n not in helper: fail(f'safe same-track duration helper missing: {n}')
block=on[on.index('elif same_loaded_for_upgrade:'):on.index('else:', on.index('elif same_loaded_for_upgrade:'))]
if 'bind_track' in block or 'auto_provisional=True' in block:
    fail('precision same-track branch can still directly rebind MediaSync')

# 4) Progressive transaction and pure-music presentation remain intact.
for n in ('自动歌词快速首屏保持事务','progressive_keep_fast','精确增强无更优结果'):
    if n not in on: fail(f'progressive retention regressed: {n}')
launch=fn('ControlPanel','_launch_current_lyrics')
for n in ('INSTRUMENTAL_CARD_HOLD_MS','_instrumental_track_card_lrc'):
    if n not in launch: fail(f'pure-music presentation regressed: {n}')
if not any(m in launch for m in ('纯音乐歌曲卡柔和入场','纯音乐歌曲卡沿用用户入场效果')): fail('pure-music card launch diagnostic missing')

# 5) Low-level seek/gesture methods remain untouched by the restore.
for name in ('_qq_poll_pointer_gesture','_kugou_poll_pointer_gesture','_kugou_commit_gesture_seek'):
    body=fn('MediaSessionSync',name)
    if 'INSTRUMENTAL-RUNTIME-V17' in body or 'QQ新曲首锚前临时时钟显示' in body:
        fail(f'low-level method polluted: {name}')

print('LYRIC PIPELINE V17 NORMAL DISPLAY RESTORE REPLAY: PASS')
print('  first metadata candidate no longer blanks a healthy lyric: PASS')
print('  confirmed QQ track can render ordinary LRC on display-only provisional local clock: PASS')
print('  precise same-track result resolves duration pending without media reset: PASS')
print('  pure-music card and progressive upgrade remain intact: PASS')
