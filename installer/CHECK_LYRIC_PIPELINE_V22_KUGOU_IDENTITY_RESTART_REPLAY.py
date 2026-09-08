#!/usr/bin/env python3
import ast, sys
from pathlib import Path
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V22_KUGOU_IDENTITY_RESTART_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def fail(msg):
    print('LYRIC PIPELINE V22 KUGOU IDENTITY + SAME-TRACK RESTART REPLAY: FAIL')
    print('  -',msg); raise SystemExit(1)
def fn(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name==name:
                    return ast.get_source_segment(src,m)
    fail(f'missing {cls}.{name}')
if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V22','INSTRUMENTAL-RUNTIME-V23','INSTRUMENTAL-RUNTIME-V24','INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')): fail('V22+ marker missing')
poll=fn('MediaSessionSync','_poll_loop')
for needle in ('prev_identity = (','next_identity = (',"next_identity != prev_identity","self._state.get('media_metadata_mono')"):
    if needle not in poll: fail(f'identity-event timestamp semantics missing: {needle}')
probe=fn('ControlPanel','_on_track_probe_result')
if "source='kugou-window-title-probe'" in probe or '_promote_kugou_background_identity_hint(' in probe:
    fail('window-title probe still has one-hit KuGou identity authority')
for needle in ('_kugou_window_probe_identity_credible','酷狗窗口探针壳层文本拒绝','identity-authority=reject'):
    if needle not in probe: fail(f'window probe rejection missing: {needle}')
cred=fn('ControlPanel','_kugou_window_probe_identity_credible')
for bad in ('酷狗音乐','菜单','主菜单','桌面歌词'):
    if bad not in cred: fail(f'known KuGou shell label not rejected: {bad}')
detected=fn('ControlPanel','_detected_player_track')
for needle in ('_kugou_window_probe_identity_credible','not self._auto_transport_hint_active()'):
    if needle not in detected: fail(f'cached window probe remains unguarded: {needle}')
# GSMTC remains the fast background identity authority.
consume=fn('ControlPanel','_consume_background_identity_fast')
for needle in ('kugou-gsmtc-fast-event','_promote_kugou_background_identity_hint'):
    if needle not in consume: fail(f'GSMTC fast identity path lost: {needle}')
host=fn('MediaSessionSync','_kugou_poll_uia_progress_v2')
for needle in ('same_track_restart','酷狗同曲重新播放时钟立即回锚',"reason=('host-uia-same-track-restart' if same_track_restart else 'host-uia-range-v2')"):
    if needle not in host: fail(f'same-track restart reanchor missing: {needle}')
for forbidden in ('LyricSearchEngine.search(', '_start_auto_search_job('):
    if forbidden in host: fail(f'Host-V2 clock path polluted network/identity authority: {forbidden}')
print('LYRIC PIPELINE V22 KUGOU IDENTITY + SAME-TRACK RESTART REPLAY: PASS')
print('  KuGou window probe cannot one-hit replace GSMTC/Host-V2 identity: PASS')
print('  MediaProperties poll time no longer masquerades as track-event time: PASS')
print('  same-track proven rail rollback reanchors clock without lyric refetch: PASS')
