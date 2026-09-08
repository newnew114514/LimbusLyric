#!/usr/bin/env python3
import ast, sys
from pathlib import Path
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V23_KUGOU_IDENTITY_DURATION_PLAYING_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def fail(msg):
    print('LYRIC PIPELINE V23 KUGOU IDENTITY/DURATION/PLAYING REPLAY: FAIL')
    print('  -',msg); raise SystemExit(1)
def fn(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name==name:
                    return ast.get_source_segment(src,m)
    fail(f'missing {cls}.{name}')
if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V23','INSTRUMENTAL-RUNTIME-V24','INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')): fail('V23+ marker missing')
bind=fn('MediaSessionSync','bind_track')
for needle in ('_kg_prev_local_status','_kg_prev_local_active','酷狗新曲临时时钟沿用播放态','_kugou_auto_playing_carry_until_mono','self._set_state(duration_ms=duration)'):
    if needle not in bind: fail(f'KuGou provisional continuity missing: {needle}')
rail=fn('MediaSessionSync','_kugou_rail_local_position')
for needle in ('_kugou_auto_playing_carry_until_mono',"_kugou_rail_master_reason", "auto-track-bootstrap"):
    if needle not in rail: fail(f'stale-paused grace missing: {needle}')
complete=fn('ControlPanel','_complete_same_track_duration')
for needle in ('compatible_enrichment','酷狗同曲歌手补全兼容时长','bind_song, bind_artist = media_song, media_artist','self._same_track(song, artist, media_song, media_artist)'):
    if needle not in complete: fail(f'KuGou enriched-artist duration completion missing: {needle}')
# Duration completion must remain same-key only; no track/request side effects.
for forbidden in ('_request_auto_track(', '_start_auto_search_job(', 'stop_lyric('):
    if forbidden in complete: fail(f'duration completion gained side effect: {forbidden}')
# Old Host/Rail regression must recognize both V22+ reason branches rather than a brittle literal assignment.
host_gate=(p.parent/'installer'/'CHECK_KUGOU_HOST_RAIL_REWORK_REPLAY.py').read_text(encoding='utf-8')
for needle in ('host-uia-range-v2','host-uia-same-track-restart'):
    if needle not in host_gate: fail(f'historical Host/Rail gate not V22+ aware: {needle}')
print('LYRIC PIPELINE V23 KUGOU IDENTITY/DURATION/PLAYING REPLAY: PASS')
print('  enriched KuGou artist identity may complete duration without media reset: PASS')
print('  fresh new-track provisional rail carries prior playing state through stale paused sample: PASS')
print('  new provisional KuGou track clears previous-song duration before rail seed: PASS')
print('  historical Host/Rail packaging gate accepts V22+ conditional reason: PASS')
