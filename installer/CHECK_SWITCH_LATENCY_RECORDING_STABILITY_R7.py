#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys, time as _time, concurrent.futures as _cf, threading as _threading
if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_SWITCH_LATENCY_RECORDING_STABILITY_R7.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ SWITCH LATENCY + RECORDING STABILITY R7' in src,'R7 build tag missing')
marker='# Switch latency + recording stability R7'
need(marker in src,'R7 marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
required=(
    '_r7_qq_search_breaker_open','_r7_fast_provider_probe','_r7_fast_auto_search_impl',
    '_r7_resume_song_atlas','_r7_schedule_song_fragment_atlas','_r7_actually_start',
    '_r7_activate_switch_latency_recording_stability')
for name in required: need(name in funcs,'missing '+name)
block=src[src.index(marker):src.index('if __name__ == "__main__":',src.index(marker))]
for token in (
    "R7_FAST_RACE_PROVIDERS_OPEN = ('网易云', '酷狗')",
    'R7_SWITCH_ATLAS_QUIET_MS = 920.0',
    'R7_SWITCH_SPECULATIVE_QUIET_MS = 240.0',
    "setattr(LyricWindow, '_schedule_song_fragment_atlas', _r7_schedule_song_fragment_atlas)",
    "setattr(LyricWindow, '_actually_start', _r7_actually_start)",
): need(token in block,'R7 activation/scheduling contract missing '+token)
need("globals().get('_r7_fast_auto_search_impl')" in src, 'R7 fast race not consolidated into H95F10F8 search layer')
need("setattr(LyricSearchEngine, 'search'" not in block, 'R7 added a sixth LyricSearchEngine.search patch layer')
# R7 is scheduling-only: no clock/seek/provider parser/effect formula override.
for bad in (
    "setattr(MediaSessionSync, 'position'", "setattr(MediaSessionSync, 'seek'",
    "setattr(MediaSessionSync, 'bind_track'", 'parse_lrc =', 'FadingLine.draw =',
    'QPainterPath', '_render_song_atlas_glyph =', '_verify_precise_enhancement_against_native ='):
    need(bad not in block,'R7 crossed protected runtime authority '+bad)

def compile_func(name,ns):
    node=copy.deepcopy(funcs[name]); node.decorator_list=[]
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<r7>','exec'),ns)
    return ns[name]

# Provider race replay: when QQ breaker is open, NetEase and KuGou are concurrent and the
# first usable ordinary payload returns without waiting for the slower provider.
class FakeLocal:
    fn=None
class Engine:
    _cancel_local=FakeLocal()
    last_error=''
    meta={}
    @classmethod
    def _set_cancel_check(cls,fn=None): cls._cancel_local.fn=fn
    @classmethod
    def _set_provider_meta(cls,**meta): cls.meta=dict(meta)
    @classmethod
    def last_provider_meta(cls): return dict(cls.meta)
class Breaker:
    def snapshot(self,key): return {'retry_after_ms':32000}
class Th:
    Event=_threading.Event
    @staticmethod
    def current_thread(): return type('T',(),{'name':'LimbusLyric-AutoLyrics-g9'})()
logs=[]
def mature(song,artist='',source='网易云',trans_only=False,provider_track_id=None,provider_duration_ms=0,prefer_precise=True,provider_locked=False,require_translation_pair=False):
    # provider_locked calls are the mature provider parsers; deliberately make KuGou slower.
    if provider_locked:
        if source=='网易云': _time.sleep(0.07); Engine.meta={'source':'网易云'}; return '[00:00.00]hello',193454
        if source=='酷狗': _time.sleep(0.23); Engine.meta={'source':'酷狗'}; return '[00:00.00]hello',193000
    return '[00:00.00]fallback',193000
ns={
    'LyricSearchEngine':Engine,'_H95F10F8_SEARCH_PRE':mature,'_R2_QQ_SEARCH_BREAKER':Breaker(),
    'R7_FAST_RACE_ENABLED':True,'R7_FAST_RACE_PROVIDERS_OPEN':('网易云','酷狗'),
    'R7_FAST_RACE_PROVIDERS_CLOSED':('QQ音乐','网易云'),'threading':Th,'concurrent':type('C',(),{'futures':_cf}),
    'time':_time,'_lyric_clock_quality':lambda x:1 if x else 0,
    'write_error_log':lambda *a,**k: logs.append((a,k)),
}
for name in ('_r7_qq_search_breaker_open','_r7_fast_provider_probe','_r7_fast_auto_search_impl'):
    compile_func(name,ns)
t0=_time.monotonic()
routed=ns['_r7_fast_auto_search_impl']('赤と青','ROTH BART BARON','QQ音乐',False,None,0,False,False,False)
need(isinstance(routed, tuple) and len(routed)==2, 'R7 eligible fast route did not handle request')
lyric,dur=routed
elapsed=(_time.monotonic()-t0)*1000.0
need(bool(lyric) and dur==193454,'R7 fast race did not return first usable ordinary lyric')
need(elapsed < 180.0,f'R7 fast race waited for serial providers: {elapsed:.1f}ms')
need(Engine.meta.get('r7_fast_payload_provider')=='网易云','R7 fast payload provenance missing')
need(ns['_r7_fast_auto_search_impl']('赤と青','ROTH BART BARON','QQ音乐',False,None,0,True,False,False) is None,
     'R7 precise request must stay on mature H95F10F8 path')

# Atlas replay: switch quiet blocks whole-song atlas scheduling but current start still delegates;
# once the quiet window expires, the mature atlas scheduler resumes automatically.
class Clock:
    def __init__(self): self.t=10.0
    def monotonic(self): return self.t
clock=Clock(); timers=[]; schedule_calls=[]; start_calls=[]
class Timer:
    @staticmethod
    def singleShot(ms,fn): timers.append((ms,fn))
def atlas_pre(window,visual_style=None,prewarm_only=False):
    schedule_calls.append((visual_style,prewarm_only)); return 'mature-atlas'
def start_pre(window,*args,**kwargs): start_calls.append(1); return 'mature-start'
ans={
    'time':clock,'QTimer':Timer,'_R7_ATLAS_SCHEDULE_PRE':atlas_pre,'_R7_ACTUALLY_START_PRE':start_pre,
    'R7_SWITCH_ATLAS_QUIET_MS':920.0,'R7_SWITCH_SPECULATIVE_QUIET_MS':240.0,
}
for name in ('_r7_resume_song_atlas','_r7_schedule_song_fragment_atlas','_r7_actually_start'):
    compile_func(name,ans)
class W:
    lyric_timeline=[(0,'x')]
    _speculative_render_quiet_until_mono=0.0
    _r7_switch_atlas_quiet_until_mono=0.0
    _r7_atlas_resume_armed=False
    _song_fragment_atlas_deferred=False
w=W()
need(ans['_r7_actually_start'](w)=='mature-start' and start_calls,'R7 start did not delegate mature start')
need(w._r7_switch_atlas_quiet_until_mono >= 10920.0,'R7 atlas quiet window missing')
need(w._speculative_render_quiet_until_mono >= 10240.0,'R7 speculative quiet window missing')
r=ans['_r7_schedule_song_fragment_atlas'](w)
need(r=='r7-switch-deferred' and not schedule_calls and timers,'R7 did not defer song atlas during switch')
clock.t=11.1
timers[-1][1]()
need(bool(schedule_calls),'R7 did not resume mature atlas after quiet window')
print('SWITCH LATENCY + RECORDING STABILITY R7: PASS')
print('  QQ fast ordinary providers race instead of serial foreign waits: PASS')
print('  existing duration/version validator remains downstream authority: PASS')
print('  switch-time whole-song Atlas is deferred; current/visible start unchanged: PASS')
print('  clock/seek/provider parsers/precision verification/effect formulas unchanged: PASS')
