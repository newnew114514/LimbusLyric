#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, queue, sys, types
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_SHARED_RENDER_WORK_SCHEDULER_H95F10F14_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ SHARED RENDER WORK SCHEDULER H95F10F14' in src,'F14 build tag missing')
marker='# H95F10F14 shared render-work scheduler'; need(marker in src,'F14 marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
req=('_h95f10f14_work_snapshot','_h95f10f14_note','_h95f10f14_admission','_h95f10f14_admit','_h95f10f14_prewarm_future_rows','_h95f10f14_work_contract','_h95f10f14_performance_contract','_h95f10f14_activate')
for n in req: need(n in funcs,'missing '+n)
def fs(n): return ast.get_source_segment(src,funcs[n]) or ''
state=fs('_h95f10f14_work_snapshot'); admission=fs('_h95f10f14_admission'); admit=fs('_h95f10f14_admit'); future=fs('_h95f10f14_prewarm_future_rows'); act=fs('_h95f10f14_activate')
for t in ("'_h61_row_worker_active'","'_song_fragment_atlas_inflight'","'_h95f10f7_translation_depth_worker'","'_h62_decay_worker_started'","'_h95f10f6_translation_blur_started'","'_h95f10f8_prewarm_queue'","'glyph_queue_depth'","'gui_install_depth'","'mature_busy'","'backlog_busy'"):
    need(t in state,'work snapshot missing '+t)
for t in ('priority <= 1',"'visible-or-current'","'mature-render-busy'","'render-backlog'","'idle-capacity'"):
    need(t in admission,'priority/admission rule missing '+t)
need("'neighbor-glyph'" in admit and '_H95F10F14_ADMIT_PRE' in admit,'F11 glyph admission not centralized')
need("'future-row-atlas'" in future and '_H95F10F14_FUTURE_PRE' in future,'future row prewarm not centralized')
for t in ("globals()['_h95f10f11_admit'] = _h95f10f14_admit","globals()['_h69_prewarm_future_rows'] = _h95f10f14_prewarm_future_rows",'LyricWindow._h95f10f14_render_work_contract','LyricWindow._h95f10f13_performance_contract = _h95f10f14_performance_contract'):
    need(t in act,'F14 activation missing '+t)
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for bad in ('threading.Thread','LyricWindow.paintEvent =','FadingLine.draw =','LyricSearchEngine.search =','MediaSessionSync.position =','MediaSessionSync.seek =','_h62_filter_shared_image(','_render_song_atlas_glyph(','QPainterPath'):
    need(bad not in block,'F14 crossed mature/runtime authority '+bad)

# Execute exact admission helpers with tiny stubs: visible/current is never denied; speculative
# work is dropped under mature work or backlog, admitted only at idle capacity.
nodes=[]
for name in ('_h95f10f14_work_snapshot','_h95f10f14_note','_h95f10f14_admission'):
    n=copy.deepcopy(funcs[name]); n.decorator_list=[]; nodes.append(n)
class Q:
    def __init__(self,n=0): self.n=n
    def qsize(self): return self.n
ns={'H95F10F14_SCHEMA':1,'H95F10F14_GLYPH_QUEUE_SOFT_LIMIT':12,'H95F10F14_INSTALL_QUEUE_SOFT_LIMIT':8,'_H95F10F9_PREWARM_QUEUE':Q(0)}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<f14>','exec'),ns)
class W:
    _h61_row_worker_active=False; _song_fragment_atlas_inflight=set(); _h95f10f7_translation_depth_worker=False
    history_lines=[]; fading_lines=[]; _h95f10f8_prewarm_queue=[]
w=W(); f=ns['_h95f10f14_admission']
need(f(w,'current',0)['allowed'] is True,'visible/current work was denied')
need(f(w,'future-row',14)['allowed'] is True,'idle speculative work was denied')
w._h61_row_worker_active=True
need(f(w,'future-row',14)['allowed'] is False and f(w,'future-row',14)['reason']=='mature-render-busy','mature work did not block speculative admission')
w._h61_row_worker_active=False; ns['_H95F10F9_PREWARM_QUEUE']=Q(12)
need(f(w,'neighbor',10)['allowed'] is False and f(w,'neighbor',10)['reason']=='render-backlog','backlog did not block speculative admission')
need(f(w,'current',1)['allowed'] is True,'current work was incorrectly blocked by backlog')
print('SHARED RENDER WORK SCHEDULER H95F10F14 REPLAY: PASS')
print('  one admission facade observes H61/Atlas/depth/blur/install backlog: PASS')
print('  visible/current render work is never denied: PASS')
print('  N+1/N+2/future-row speculation yields under contention: PASS')
print('  no new worker/effect/provider/clock owner introduced: PASS')
