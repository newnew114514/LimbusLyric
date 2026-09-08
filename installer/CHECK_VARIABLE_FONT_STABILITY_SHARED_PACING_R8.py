#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys
if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_VARIABLE_FONT_STABILITY_SHARED_PACING_R8.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ VARIABLE FONT STABILITY + SHARED FRAME PACING R8' in src,'R8 lineage missing')
need('# Variable-font stability + shared frame pacing R8' in src,'R8 marker missing')
# R8 field evidence remains useful, but its false-fuse/history-freeze controls were proven
# unsafe in production. R9 must be present and must supersede those runtime owners.
need('+ VISUAL CONTINUITY + FRAME BUDGET R9' in src,'R9 corrective layer missing')
need("globals()['_r8_freeze_history_row'] = _r9_freeze_history_row" in src,'R9 did not supersede history freeze')
need('FadingLine.update_hold = _r9_update_hold' in src,'R9 did not restore mature held-row motion')
need("LyricWindow._schedule_song_fragment_atlas = _r9_schedule_song_fragment_atlas" in src,'R9 did not supersede R8 atlas admission')
r9=src[src.index('# Visual continuity + frame-budget R9'):src.index('if __name__ == "__main__":',src.index('# Visual continuity + frame-budget R9'))]
need("_song_fragment_atlas_performance_fused = True" not in r9,'R9 reintroduced false performance fuse')
need("return 'r9-variable-size-no-song-prewarm'" in r9,'R9 variable-size admission marker missing')
need("row._r8_hold_geometry_frozen = False" in r9,'R9 does not unfreeze mature history motion')
for bad in ('MediaSessionSync.', 'LyricSearchEngine.', "'QQ音乐'", "'网易云'", "'酷狗'", 'qqmusic.exe', 'cloudmusic', 'kugou'):
    need(bad not in r9,'R9 corrective renderer crossed player/provider boundary: '+bad)
print('VARIABLE FONT STABILITY + SHARED FRAME PACING R8: PASS (superseded safely by R9)')
print('  R8 false-fuse/history-freeze regression is explicitly retired: PASS')
print('  all-player shared renderer boundary remains intact: PASS')
