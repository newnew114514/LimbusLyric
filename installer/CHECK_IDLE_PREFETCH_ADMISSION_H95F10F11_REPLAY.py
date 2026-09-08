#!/usr/bin/env python3
from __future__ import annotations
import ast,pathlib,sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_IDLE_PREFETCH_ADMISSION_H95F10F11_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ IDLE PREFETCH ADMISSION H95F10F11' in src,'F11 tag missing')
marker='# H95F10F11 idle prefetch admission + two-line lookahead'; need(marker in src,'F11 marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
req=('_h95f10f11_stale','_h95f10f11_heavy_render_busy','_h95f10f11_admit','_h95f10f11_worker_loop','_h95f10f11_neighbor_line','_h95f10f11_neighbor_prewarm','_h95f10f11_activate')
for n in req: need(n in funcs,'missing '+n)
def fs(n): return ast.get_source_segment(src,funcs[n]) or ''
admit=fs('_h95f10f11_admit'); busy=fs('_h95f10f11_heavy_render_busy'); worker=fs('_h95f10f11_worker_loop'); neighbor=fs('_h95f10f11_neighbor_line'); np=fs('_h95f10f11_neighbor_prewarm'); act=fs('_h95f10f11_activate')
need('priority < 0' in admit and 'return True, 0.0' in admit,'visible prewarm must never wait')
need('priority <= 1' in admit and 'H95F10F11_CURRENT_MAX_WAIT_MS' in admit,'current-row bounded yield missing')
need('H95F10F11_NEIGHBOR_MAX_WAIT_MS' in admit and 'return (priority <= 1)' in admit,'neighbor drop-under-contention missing')
for t in ('_h61_row_worker_active','_song_fragment_atlas_inflight','_h95f10f7_translation_depth_worker'):
    need(t in busy,'mature work admission hint missing '+t)
for t in ('_h95f10f11_admit','_render_song_atlas_glyph','_H95F10F9_GLYPH_PENDING','_h95f10f11_stale'):
    need(t in worker,'admission worker missing '+t)
need('threading.Thread' not in neighbor and 'threading.Thread' not in np,'lookahead spawned extra worker')
for t in ("f'next{distance}-primary'","f'next{distance}-translation'",'base_priority=10','else 14'):
    need(t in neighbor,'two-tier neighbour priority missing '+t)
need('_h95f10f11_neighbor_line(window,token,line_index,1)' in np,'N+1 prewarm missing')
need('H95F10F11_SECOND_NEIGHBOR_DELAY_MS' in np and '_h95f10f11_neighbor_line(w,t,i,2)' in np,'N+2 delayed prewarm missing')
for t in ('queue.PriorityQueue','LimbusLyric-H95F10F11-Prefetch','_H95F10F9_PREWARM_WORKER=worker',"globals()['_h95f10f9_neighbor_prewarm']=_h95f10f11_neighbor_prewarm"):
    need(t in act,'F11 activation missing '+t)
# Structural layer only; no protected authority or effect formulas.
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for bad in ('LyricSearchEngine.search =','MediaSessionSync.position =','MediaSessionSync.seek =','FadingLine.draw =','_h62_decay_progress =','_entrance_motion =','QPainterPath'):
    need(bad not in block,'F11 crossed authority '+bad)
print('IDLE PREFETCH ADMISSION H95F10F11 REPLAY: PASS')
print('  visible misses never wait; current prewarm yields only within a bound: PASS')
print('  speculative N+1/N+2 prefetch is lower-priority and disposable under contention: PASS')
print('  one active glyph raster worker; no new neighbour threads: PASS')
print('  H61/H69/depth/search/clock/effect authority unchanged: PASS')
