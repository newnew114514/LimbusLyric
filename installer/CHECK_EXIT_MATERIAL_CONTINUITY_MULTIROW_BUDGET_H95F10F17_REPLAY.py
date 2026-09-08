#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_EXIT_MATERIAL_CONTINUITY_MULTIROW_BUDGET_H95F10F17_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ EXIT MATERIAL CONTINUITY + MULTIROW BUDGET H95F10F17' in src,'F17 build tag missing')
marker='# H95F10F17 exit material continuity + multi-row render budget'
need(marker in src,'F17 marker missing')
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name in (
    '_h95f10f17_draw_history_material','_h95f10f17_draw_active_primary_cache_only',
    '_h95f10f17_draw_active_translation_cache_only','_h95f10f17_paint_core',
    '_h95f10f17_make_history_pre','_h95f10f17_prime_ready',
    '_h95f10f17_visible_material_backlog','_h95f10f17_h61_schedule',
    '_h95f10f17_log_style','_h95f10f17_activate'):
    need(name in funcs,'missing '+name)
# F17 must stay on renderer admission/material continuity only.
for bad in (
    'MediaSessionSync.position =','MediaSessionSync.seek =','MediaSessionSync.bind_track =',
    'LyricSearchEngine.search =','ControlPanel._request_auto_track =','ControlPanel._monitor_track_change =',
    'FadingLine.draw =','requests.','threading.Thread','QPainterPath','QImage.filter'):
    need(bad not in block,'F17 crossed protected authority '+bad)
# A translation-only miss must leave mature primary/history intact.
need('if pm<=0:' in block and "route='translation-local-cold'" in block,'translation-local cold route missing')
need('window._h95f10f9_suppress_legacy_translation=True' in block,'translation-only suppression missing')
need("route='primary-glyph-local-cold'" in block,'primary glyph-local cold route missing')
need('whole-frame-plain=0' in block and 'history-material=preserved' in block,'whole-frame downgrade retirement not explicit')
need("globals()['_h35_draw_plain_history_rows']=_h95f10f17_draw_history_material" in block,'history material continuity hook missing')
need("globals()['_h95f10f8_prime_one']=_h95f10f17_prime_ready" in block,'budgeted GUI install hook missing')
need("globals()['_h61_schedule_row_atlas']=_h95f10f17_h61_schedule" in block,'H61 visible-material yield hook missing')
need('H95F10F17_GUI_INSTALL_BUDGET_MS = 1.35' in block and 'H95F10F17_GUI_INSTALL_MAX = 5' in block,'bounded multi-glyph install contract drifted')
need("row.mode='chinese'" in block and '_h95f10f17_optical_material_alpha=True' in block,'history optical alpha continuity missing')
need('stroke=' in block and 'glow=' in block and 'glow_alpha=' in block,'style/color diagnostic incomplete')

# Replay the H61 admission contract without Qt: visible material backlog blocks current-row
# H61 and, once clear, delegates to the mature scheduler unchanged.
def compile_func(name, ns):
    node=copy.deepcopy(funcs[name]); node.decorator_list=[]
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<f17>','exec'),ns)
    return ns[name]
compile_func('_h95f10f17_visible_material_backlog',{})
backlog_ns={'_h95f10f17_visible_material_backlog':None}
# Recompile into one namespace so the scheduler sees the helper.
ns={}
compile_func('_h95f10f17_visible_material_backlog',ns)
class Clock:
    def __init__(self): self.t=10.0
    def monotonic(self): return self.t
clock=Clock(); calls=[]
def pre(window,text): calls.append((window,text)); return 'mature-scheduled'
ns.update({'time':clock,'H95F10F17_H61_VISIBLE_DEFER_MS':84.0,'_H95F10F17_H61_SCHEDULE_PRE':pre})
compile_func('_h95f10f17_h61_schedule',ns)
class W: pass
w=W(); w.full_text='current'; w._h95f10f10_render_plan={'primary_visible_missing':1,'translation_visible_missing':0}; w._h95f10f8_prewarm_queue=[]
r=ns['_h95f10f17_h61_schedule'](w,'current')
need(r=='deferred-visible-material' and not calls,'current H61 did not yield to visible missing material')
w._h95f10f10_render_plan={'primary_visible_missing':0,'translation_visible_missing':0}; w._h95f10f8_prewarm_queue=[]
r=ns['_h95f10f17_h61_schedule'](w,'current')
need(r=='mature-scheduled' and len(calls)==1,'H61 did not delegate after visible material backlog cleared')
# Future/non-current rows must still delegate to F14/mature ownership even with current backlog.
w._h95f10f10_render_plan={'primary_visible_missing':2,'translation_visible_missing':1}
r=ns['_h95f10f17_h61_schedule'](w,'future')
need(r=='mature-scheduled' and len(calls)==2,'future H61 admission was stolen from mature/F14 owner')

# History creation retains the original mode as metadata but switches the history renderer to
# optical material alpha, eliminating the old face alpha-100 split only for resident history.
class Row:
    def __init__(self): self.mode='english'
def history_pre(window,text): return Row()
hns={'_H95F10F17_HISTORY_PRE':history_pre}
compile_func('_h95f10f17_make_history_pre',hns)
row=hns['_h95f10f17_make_history_pre'](object(),'hello')
need(row.mode=='chinese','history row did not use optical material alpha path')
need(row._h95f10f17_original_mode=='english','original history mode was not preserved as metadata')
need(row._h95f10f17_optical_material_alpha is True,'history optical alpha marker missing')

print('EXIT MATERIAL CONTINUITY + MULTIROW BUDGET H95F10F17 REPLAY: PASS')
print('  translation-only cold miss cannot downgrade primary/history: PASS')
print('  resident history uses existing optical material; western face-alpha split retired for history: PASS')
print('  visible material backlog makes current H61 yield; future-row ownership unchanged: PASS')
print('  GUI installs are time-bounded multi-glyph drains; paint raster/path build remains forbidden: PASS')
print('  provider/search/clock/seek/effect-progress authority unchanged: PASS')
