from __future__ import annotations
import ast, sys
from pathlib import Path

if len(sys.argv)!=2:
    print('usage: CHECK_KUGOU_HANDOFF_UI_CLEANUP_REPLAY.py <main.py>'); raise SystemExit(2)
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8'); tree=ast.parse(source,filename=str(path))
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name in ('_kugou_host_candidate_score','_kugou_range_clock_candidate'):
    if name not in funcs:
        raise SystemExit('KUGOU HANDOFF/UI CLEANUP REPLAY: FAIL missing '+name)
ns={}
mod=ast.Module(body=[funcs['_kugou_host_candidate_score'],funcs['_kugou_range_clock_candidate']],type_ignores=[]); ast.fix_missing_locations(mod)
exec(compile(mod,str(path),'exec'),ns)
score=ns['_kugou_host_candidate_score']; clock=ns['_kugou_range_clock_candidate']

# Never select LimbusLyric/desktop/other app windows when KuGou has disappeared.
assert score('Qt5152QWindowToolSaveBits','歌词悬浮窗',(0,0,1920,1045),True,False) < -10000
assert score('Progman','Program Manager',(0,0,1920,1045),True,False) < -10000
assert score('kugou_ui','周杰伦 - 晴天 - 酷狗音乐',(667,108,1727,828),True,False) > 1000
assert score('kugou_mv_win','酷狗MV',(700,150,1600,800),True,False) < -10000

# Same-track normal read: 2971 centiseconds => 29.710 s and no duration mismatch.
r=clock('Slider',2971,0,26900,269000)
assert r and abs(r['observed_ms']-29710) < 1 and not r['native_mismatch']
# Old lyric epoch sees a new 221 s Slider: detect the transition, do not interpret it as old-song seek.
r=clock('Slider',0,0,22100,269000)
assert r and r['native_mismatch'] and int(r['native_duration_ms'])==221000 and int(r['observed_ms'])==0
# After bind_track clears the old duration, the same range immediately provides new-song absolute time+duration.
r=clock('Slider',2925,0,22100,0)
assert r and int(r['duration_ms'])==221000 and int(r['observed_ms'])==29250
# A percent/volume slider cannot bootstrap a no-duration track.
assert clock('Slider',55,0,100,0) is None

# Product cleanup: no compact-mode UI/config, no disable-able loop protection.
for forbidden in ('简洁模式','compact_mode_btn','loop_check','循环边界保护（推荐）'):
    assert forbidden not in source, forbidden
assert source.count('self.lyric_window.loop = True') >= 2
assert "'compact_mode':" not in source and "'loop': panel." not in source
assert 'kugou-host-v2-title' in source and '酷狗宿主V2原生Range时长接管' in source
print('KUGOU HANDOFF/UI CLEANUP REPLAY: PASS')
print('  strict official KuGou host selection: PASS')
print('  native RangeValue transition clock/duration: PASS')
print('  compact mode removed + loop guard forced on: PASS')
