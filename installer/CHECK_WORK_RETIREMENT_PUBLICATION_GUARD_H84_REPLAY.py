"""H84: bounded row-work retirement + final player publication ownership guard."""
import ast, sys, threading, time
from pathlib import Path
from collections import OrderedDict
from types import SimpleNamespace as NS
sys.dont_write_bytecode=True
root=Path(sys.argv[1]).resolve()
main=next(root.glob('LimbusLyric_*.py'))
src=main.read_text(encoding='utf-8')
tree=ast.parse(src)
top={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
media=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='MediaSessionSync')
methods={n.name:n for n in media.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
checks=[]
def ck(name,v,detail=''):
    checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name+((': '+str(detail)) if detail else ''),flush=True)
def load(nodes,ns): exec(compile(ast.Module(body=nodes,type_ignores=[]),str(main),'exec'),ns)

ck('H84 build tag present','+ WORK RETIREMENT + PUBLICATION GUARD H84' in src)
ck('H84 stable scope keeps broad async single-slot disabled','H84_ASYNC_SINGLE_SLOT_ENABLED = False' in src and '_poll_owned_media_request' not in src)
poll_src=ast.get_source_segment(src,methods['_poll_loop']) or ''
ck('poll captures player epoch/process before slow reads',"poll_owner = (int(getattr(self, '_media_player_epoch'" in poll_src and 'source = poll_owner[1]' in poll_src)
ck('synchronous WinRT request model deliberately preserved',
   'manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()' in poll_src and
   'props = await session.try_get_media_properties_async()' in poll_src)
ck('late iteration is checked before provider/clock merge',poll_src.count("poll_owner != (\n")>=3)
ck('final state publication carries captured owner','self._set_state(_poll_owner=poll_owner, **update)' in poll_src)

# Base _set_state stays legacy-identical; execute H84's outer publication wrapper in isolation.
base_set_src=ast.get_source_segment(src,methods['_set_state']) or ''
ck('legacy _set_state body remains free of H84 owner logic', '_poll_owner' not in base_set_src)
def _base_set_state(sync, **kwargs):
    with sync._lock:
        if 'position_ms' in kwargs and kwargs.get('position_ms') is not None:
            kwargs.setdefault('position_anchor_mono', time.monotonic() * 1000.0)
        sync._state.update(kwargs); sync._state['updated_at']=time.time()
ns={'time':time,'_h84_set_state_pre':_base_set_state}
load([top['_h84_set_state']],ns)
class Sync:
    def __init__(self):
        self._lock=threading.Lock(); self._stop_event=threading.Event(); self._media_player_epoch=7
        self._process_hint='cloudmusic'; self._state={'title':'NEW','position_ms':3000}
s=Sync(); old=dict(s._state)
accepted=ns['_h84_set_state'](s,_poll_owner=(7,'cloudmusic'),title='CURRENT',position_ms=3200)
ck('matching owner publishes normally',accepted is True and s._state.get('title')=='CURRENT' and s._state.get('position_ms')==3200)
old=dict(s._state); rejected=ns['_h84_set_state'](s,_poll_owner=(6,'qqmusic'),title='STALE QQ',position_ms=60000)
ck('old player/epoch publication is rejected',rejected is False and s._state==old)
s._media_player_epoch=8; old=dict(s._state)
rejected=ns['_h84_set_state'](s,_poll_owner=(7,'cloudmusic'),title='ABA STALE')
ck('same process ABA switch still rejects old epoch',rejected is False and s._state==old)
s._stop_event.set(); old=dict(s._state)
rejected=ns['_h84_set_state'](s,_poll_owner=(8,'cloudmusic'),title='AFTER STOP')
ck('stopped worker cannot publish a final late sample',rejected is False and s._state==old)

# Execute real row queue / H82 prewarm functions without starting a worker thread.
need=['_h61_row_key','_h61_held_row_key','_h61_row_cache_init','_h84_prune_row_queue',
      '_h61_kick_row_worker','_h61_schedule_row_atlas','_h82_timeline_epoch','_h82_prewarm_future_rows']
ns=dict(OrderedDict=OrderedDict,time=time,H61_ROW_CACHE_MAX_ENTRIES=12,H61_ROW_CACHE_MAX_PIXELS=18*1024*1024,
        H61_ROW_WORKER_BUDGET_MS=420.0,H69_FUTURE_ROW_PREWARM=12,H84_ROW_QUEUE_LIMIT=36,
        _fragment_style_signature=lambda font,*a:font,write_error_log=lambda *a,**kw:None)
load([top[n] for n in need],ns)
class W:
    def __init__(self):
        self.full_text=''; self.history_lines=[]; self.fading_lines=[]; self.displayed_line_index=-1
        self.lyric_timeline=[(i*1000,f'line {i}') for i in range(20)]
        self._song_fragment_atlas_performance_fused=True; self.style='A'; self._h61_row_worker_active=True
    def _current_fragment_style_signature(self): return self.style
w=W()
a=ns['_h82_prewarm_future_rows'](w)
ck('initial future prewarm is bounded to 12',a==12 and len(w._h61_row_atlas_queue)==12,(a,len(w._h61_row_atlas_queue)))
# Same style/timeline should remain deduped.
a2=ns['_h82_prewarm_future_rows'](w)
ck('same style/timeline does not rebuild future work',a2==0 and len(w._h61_row_atlas_queue)==12)
# Style B retires A queue and schedules B only.
w.style='B'; b=ns['_h82_prewarm_future_rows'](w)
ck('style switch retires obsolete queued material',b==12 and len(w._h61_row_atlas_queue)==12 and all(job[2]=='B' for job in w._h61_row_atlas_queue))
# A->B->A must clear seen for A, otherwise H82/Codex interaction would starve future prewarm.
w.style='A'; a3=ns['_h82_prewarm_future_rows'](w)
ck('A-B-A style return reschedules current-style future rows',a3==12 and len(w._h61_row_atlas_queue)==12 and all(job[2]=='A' for job in w._h61_row_atlas_queue))
# Visible current row must outrank future prewarm.
w.full_text='urgent current row'; state=ns['_h61_schedule_row_atlas'](w,w.full_text)
ck('visible current row is first in bounded queue',state=='scheduled' and w._h61_row_atlas_queue[0][1]=='urgent current row')
# A retired timeline has no useful queue. This is the same wanted-set used by cooperative cancel_check.
w.full_text=''; w.lyric_timeline=[]; w.history_lines=[]; w.fading_lines=[]
ns['_h84_prune_row_queue'](w)
ck('retired timeline clears queued work and wanted set',not w._h61_row_atlas_queue and not w._h61_row_wanted_keys)
# Verify stop_lyric contains the immediate retirement hook (full method is too UI-heavy to instantiate here).
lyric=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='LyricWindow')
stop=next(n for n in lyric.body if isinstance(n,ast.FunctionDef) and n.name=='stop_lyric')
stop_src=ast.get_source_segment(src,stop) or ''
ck('stop_lyric immediately retires row queue and H82 seen epoch',
   'self._h61_row_atlas_queue = []' in stop_src and 'self._h61_row_wanted_keys = frozenset()' in stop_src and
   'self._h82_prewarm_epoch = None' in stop_src and 'self._h82_prewarm_seen = set()' in stop_src)
worker_src=ast.get_source_segment(src,top['_h61_kick_row_worker']) or ''
ck('active row worker cooperatively cancels once key is no longer wanted',
   "if key not in getattr(window, '_h61_row_wanted_keys', ())" in worker_src)

note=root/'WORK_RETIREMENT_PUBLICATION_GUARD_H84_NOTE_20260906.md'
ck('H84 note present',note.is_file())
passed=sum(checks)
print(f'H84 WORK RETIREMENT + PUBLICATION GUARD: {passed}/{len(checks)} PASS')
raise SystemExit(0 if passed==len(checks) else 1)
