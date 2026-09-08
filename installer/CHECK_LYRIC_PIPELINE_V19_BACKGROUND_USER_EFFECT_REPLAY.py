#!/usr/bin/env python3
import ast, sys
from pathlib import Path
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V19_BACKGROUND_USER_EFFECT_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def fail(msg):
    print('LYRIC PIPELINE V19 BACKGROUND + USER EFFECT REPLAY: FAIL'); print('  -',msg); raise SystemExit(1)
def fn(cls,name):
    for node in tree.body:
        if isinstance(node,ast.ClassDef) and node.name==cls:
            for item in node.body:
                if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)) and item.name==name:
                    return ast.get_source_segment(src,item)
    fail(f'missing {cls}.{name}')
if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V19','INSTRUMENTAL-RUNTIME-V20','INSTRUMENTAL-RUNTIME-V21','INSTRUMENTAL-RUNTIME-V22','INSTRUMENTAL-RUNTIME-V23','INSTRUMENTAL-RUNTIME-V24','INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')): fail('V19+ marker missing')
# Intro/title/card rows must no longer force a private soft/no-shake mode.
vis=fn('LyricWindow','_ordinary_visual_state')
if "_flow_mode = 'intro-credit-soft'" in vis: fail('intro rows still force intro-credit-soft')
if "body.lstrip().startswith('♫ ')" in vis: fail('synthetic title still has dedicated visual branch')
if '_entrance_effect_for_text' not in vis: fail('ordinary rows no longer use user entrance effect')
launch=fn('ControlPanel','_launch_current_lyrics')
for n in ('纯音乐歌曲卡沿用用户入场效果','entrance_effect_combo','western_entrance_effect_combo','INSTRUMENTAL_CARD_HOLD_MS'):
    if n not in launch: fail(f'user-effect track card route missing: {n}')
if '纯音乐歌曲卡柔和入场' in launch: fail('old forced track-card fade remains')
# KuGou background identity may skip only debounce after process-affine metadata evidence.
promote=fn('ControlPanel','_promote_kugou_background_identity_hint')
for n in ('酷狗后台新曲身份立即接管','debounce=skip','clock-authority=unchanged','_note_auto_transport_hint','_request_auto_track','self._auto_candidate_since = evidence_sec'):
    if n not in promote: fail(f'KuGou background one-hit helper missing: {n}')
probe=fn('ControlPanel','_on_track_probe_result')
if any(m in src for m in ('INSTRUMENTAL-RUNTIME-V22','INSTRUMENTAL-RUNTIME-V23','INSTRUMENTAL-RUNTIME-V24','INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')):
    for n in ('_cached_track_probe','_kugou_window_probe_identity_credible','酷狗窗口探针壳层文本拒绝'):
        if n not in probe: fail(f'V22 safe title-probe fallback missing: {n}')
    if "source='kugou-window-title-probe'" in probe or '_promote_kugou_background_identity_hint(' in probe:
        fail('V22 window-title probe regained one-hit identity authority')
else:
    for n in ('_cached_track_probe','kugou-window-title-probe','_promote_kugou_background_identity_hint'):
        if n not in probe: fail(f'fresh title-probe fast path missing: {n}')
front=fn('ControlPanel','_refresh_frontend_status')
for n in ('kugou-gsmtc-title-change','_source_matches_process_hint','_promote_kugou_background_identity_hint'):
    if n not in front: fail(f'process-affine GSMTC background fast path missing: {n}')
# New fast-stage presentation cannot inherit previous song duration.
on=fn('ControlPanel','_on_auto_lyric_result')
for n in ('新曲快速首屏清除旧展示时长','self.lyric_window.song_duration = 0','media-authority=unchanged'):
    if n not in on: fail(f'old presentation-duration isolation missing: {n}')
# Provider clocks / seek cores stay isolated.
for name in ('_kugou_poll_pointer_gesture','_kugou_commit_gesture_seek','_qq_poll_pointer_gesture'):
    body=fn('MediaSessionSync',name)
    if '酷狗后台新曲身份立即接管' in body or '新曲快速首屏清除旧展示时长' in body:
        fail(f'low-level clock/seek method polluted: {name}')
print('LYRIC PIPELINE V19 BACKGROUND + USER EFFECT REPLAY: PASS')
print('  intro/title/track-card rows inherit user entrance/shake settings: PASS')
print('  KuGou background process-affine title evidence skips generic debounce only: PASS')
print('  new fast-stage presentation duration cannot leak from previous track: PASS')
print('  low-level clock/seek authority remains isolated: PASS')
