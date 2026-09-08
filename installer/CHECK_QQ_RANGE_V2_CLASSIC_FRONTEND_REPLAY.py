from __future__ import annotations
import ast, sys
from pathlib import Path

if len(sys.argv)!=2:
    print('usage: CHECK_QQ_RANGE_V2_CLASSIC_FRONTEND_REPLAY.py <main.py>'); raise SystemExit(2)
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8'); tree=ast.parse(source,filename=str(path))
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
name='_qq_range_progress_proof_step'
if name not in funcs: raise SystemExit('QQ RANGE V2 + CLASSIC FRONTEND REPLAY: FAIL missing '+name)
ns={'QQ_RANGE_V2_MIN_PROOF_SPAN_MS':650.0}
mod=ast.Module(body=[funcs[name]],type_ignores=[]); ast.fix_missing_locations(mod)
exec(compile(mod,str(path),'exec'),ns)
step=ns[name]

def run(values,times,status='playing'):
    p=None; proven=False
    for v,t in zip(values,times): p,proven=step(p,v,t,status,'slider')
    return p,proven

# Real playback-like movement proves in three coherent samples / >=650 ms.
p,ok=run([10000,10420,10840],[1000,1420,1840])
assert ok and int(p['count'])>=3
# A genuine song starting at exactly zero must also prove.
p,ok=run([0,420,840],[1000,1420,1840])
assert ok
# Static volume cannot prove while playing.
p,ok=run([50000,50000,50000,50000],[1000,1400,1800,2200])
assert not ok
# A fast animated/non-playback slider cannot prove.
p,ok=run([10000,15000,22000],[1000,1400,1800])
assert not ok
# Paused freeze alone is deliberately insufficient to establish playback identity.
p=None; ok=False
for t in (1000,1400,1800,2200): p,ok=step(p,12000,t,'paused','slider')
assert not ok

# Architecture/source guards: old QQ Text adapter stays fallback; RangeV2 upgrades outside it.
for token in ('QQ_RANGE_V2_ENABLED','QQ RangeV2实时进度接管','qq=range-v2','range_hit = self._try_qq_uia_range_v2'):
    assert token in source, token
assert "observed += 420.0" in source, 'do not mix Text-offset changes into this diagnostic build'
# Classic paged workbench is the only public layout; no selector/config/tray surface remains.
for forbidden in ('前端布局：','侧栏工作台','专注面板',"'frontend_mode': panel.frontend_mode_combo",'menu.addMenu("前端布局")'):
    assert forbidden not in source, forbidden
assert "def _current_frontend_mode(self):\n        # Classic paged workbench is the only public frontend.\n        return 'tabs'" in source
print('QQ RANGE V2 + CLASSIC FRONTEND REPLAY: PASS')
print('  transport proof rejects static/fast false sliders: PASS')
print('  Text fallback unchanged in this build: PASS')
print('  classic paged workbench is the only public layout: PASS')
