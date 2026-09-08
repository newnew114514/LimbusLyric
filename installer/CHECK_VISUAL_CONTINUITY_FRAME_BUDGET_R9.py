#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys, threading
from types import SimpleNamespace
if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_VISUAL_CONTINUITY_FRAME_BUDGET_R9.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ VISUAL CONTINUITY + FRAME BUDGET R9' in src,'R9 build tag missing')
marker='# Visual continuity + frame-budget R9'
need(marker in src,'R9 marker missing')
block=src[src.index(marker):src.index('if __name__ == "__main__":',src.index(marker))]
for token in (
    'R9_VISIBLE_GLYPH_BATCH = 6',
    "return 'r9-variable-size-no-song-prewarm'",
    "row._r8_hold_geometry_frozen = False",
    "FadingLine.update_hold = _r9_update_hold",
    "globals()['_h95f10f9_schedule_plan'] = _r9_h95f10f9_schedule_plan",
    'outline/glow/entrance/exit=restored',
): need(token in block,'R9 contract missing '+token)
need('_song_fragment_atlas_performance_fused = True' not in block,'R9 uses performance fuse as admission flag')
# H51 must survive ordinary->precise start_lyric hot upgrades without rerolling existing rows.
start=src[src.index('def h51_start_lyric'):src.index('def h51_queue_visual_style',src.index('def h51_start_lyric'))]
need("if not isinstance(getattr(window, '_h51_line_size_cache', None), OrderedDict):" in start,'H51 start no longer preserves existing cache')
need('window._h51_line_size_cache = OrderedDict()' in start,'H51 missing first-use cache initialization')
need('while len(size_cache) > 384' in src,'H51 cache too small for precise hot-upgrade stability')
# No player/provider special-case in the R9 renderer policy.
for bad in ('MediaSessionSync.', 'LyricSearchEngine.', "'QQ音乐'", "'网易云'", "'酷狗'", 'qqmusic.exe', 'cloudmusic', 'kugou'):
    need(bad not in block,'R9 crossed player/provider boundary: '+bad)
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
def compile_func(name,ns):
    node=copy.deepcopy(funcs[name]); node.decorator_list=[]
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<r9>','exec'),ns)
    return ns[name]
# Admission replay: variable-size must skip whole-song prewarm without arming emergency/fuse.
calls=[]
def pre(w,visual_style=None,prewarm_only=False): calls.append(1); return 'mature'
ns={'_r8_variable_size_mode':lambda w: True,'_r9_clear_r8_false_fuse':lambda w: setattr(w,'cleared',True),
    '_R9_SCHEDULE_PRE':pre}
sched=compile_func('_r9_schedule_song_fragment_atlas',ns)
w=SimpleNamespace(_song_fragment_atlas_desired_key='x',_song_fragment_atlas_pending_key='x',_song_fragment_atlas_deferred=True,
                  _song_fragment_atlas_performance_fused=False)
need(sched(w)=='r9-variable-size-no-song-prewarm','R9 variable-size schedule did not skip song prewarm')
need(not calls and not w._song_fragment_atlas_performance_fused,'R9 variable-size admission armed/called performance path')
# Held-row motion replay: history must delegate to mature owner instead of freezing.
hold=[]
ns2={'_R9_HOLD_PRE':lambda row:(hold.append(1) or True)}
upd=compile_func('_r9_update_hold',ns2)
need(upd(SimpleNamespace()) is True and len(hold)==1,'R9 did not restore mature held-row motion')
# Visible prewarm replay: <=6 current-visible glyphs per lane, no full-row or neighbour jobs.
jobs=[]
lock=threading.Lock()
ns3={
    '_r8_variable_size_mode':lambda w: True,'time':SimpleNamespace(monotonic=lambda:10.0),
    '_r9_uncached_visible_batch':lambda style,chars:tuple(chars or ())[:6],
    '_h95f10f9_enqueue_missing':lambda w,style,chars,lane,priority: jobs.append((lane,tuple(chars),priority)) or len(tuple(chars)),
    '_R9_F9_SCHEDULE_PRE':None,
}
planfn=compile_func('_r9_h95f10f9_schedule_plan',ns3)
ww=SimpleNamespace()
plan={'now':10000.0,'token':'t','primary_style':'p','translation_style':'t','primary_visible_missing_chars':tuple('abcdefghij'),
      'translation_visible_missing_chars':tuple('123456789'),'primary_missing':tuple('FULLROW'),'translation_missing':tuple('FULLTRANS')}
planfn(ww,plan)
need([j[0] for j in jobs]==['primary-visible','translation-visible'],'R9 queued speculative/full-row glyph work')
need(all(len(j[1])<=6 for j in jobs),'R9 visible glyph batch exceeded limit')
print('VISUAL CONTINUITY + FRAME BUDGET R9: PASS')
print('  same-track precise hot upgrade keeps per-line size cache: PASS')
print('  false performance fuse / plain-glyph emergency regression retired: PASS')
print('  mature history and exit motion restored: PASS')
print('  variable-size prewarm limited to small current-visible batches: PASS')
print('  shared all-player renderer scope preserved: PASS')
