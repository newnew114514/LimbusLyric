from pathlib import Path
import ast, hashlib, math, sys, time
from collections import OrderedDict
if len(sys.argv)<2: raise SystemExit('usage: CHECK_RENDER_WORK_CONSOLIDATION_H82_REPLAY.py <main.py>')
main=Path(sys.argv[1]); src=main.read_text(encoding='utf-8'); root=main.parent

def fail(msg): raise SystemExit('H82 FAIL: '+msg)
def need(tok,label=None):
    if tok not in src: fail('missing '+(label or tok))

need('+ RENDER WORK CONSOLIDATION H82','build tag')
need('# H82 render work consolidation / preview cadence / startup lyric witness closure','marker')
if not (src.rindex("if '_h81_activate_runtime' in globals():") < src.rindex("if '_h82_activate_runtime' in globals():")):
    fail('H82 must activate after H81')
block_start=src.index('# H82 render work consolidation / preview cadence / startup lyric witness closure')
block_end=src.index('# H84 work retirement + publication guard', block_start)
block=src[block_start:block_end]
for tok in (
    'timer.setTimerType(Qt.PreciseTimer)',
    'return max(16, min(34, int(round(1000.0 / hz))))',
    'def _h82_preview_centered_path(stage, text, font):',
    "cache = OrderedDict(); stage._h82_preview_path_cache = cache",
    'def _h82_prewarm_future_rows(window, anchor_index=None):',
    "window._h82_prewarm_seen = set()",
    "if key in seen:",
    "state in ('scheduled', 'cache-hit', 'inflight', 'queued')",
    'def _h82_qq_startup_existing_duration(panel, job, cancel_check=None):',
    "if not bool(j.get('startup_existing_attach')):",
    "role=lyric-version-witness | transport=unchanged",
): need(tok)
for bad in (
    'MediaSessionSync._merge_uia_position =', 'MediaSessionSync.bind_track =',
    'AsyncPlayerUiPositionReader.poll =', 'LyricSearchEngine.search =',
    'FadingLine.update =', 'FadingLine.draw ='
):
    if bad in block: fail('crossed protected runtime boundary: '+bad)

# Transport bodies are locked to the reviewed R2/R2.4 authority revisions inherited from H81.
tree=ast.parse(src)
expected={
    ('MediaSessionSync','_merge_uia_position'):'68176b714fc017d3de0fc4e2532338b3c990d74f1c1ac9a07d2dbc575874427e',
    ('MediaSessionSync','bind_track'):'7c7afbadaca51929f4eb956ad076fef14d2c053092daabdea5f34d47e5c55bf1',
    ('AsyncPlayerUiPositionReader','poll'):'92770397d6a1bb865da4a3493ba34f9ef8305a761495dc0ed4845c3f44cbc3ad',
    ('ControlPanel','_request_auto_track'):'1e02663985fe99d92ec50267ba63a050cbb3538bd698b445ffddbbc20bf47353',
}
for (cls,fn),digest in expected.items():
    node=None
    for top in tree.body:
        if isinstance(top,ast.ClassDef) and top.name==cls:
            node=next((x for x in top.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==fn),None)
            break
    if node is None: fail(f'missing protected body {cls}.{fn}')
    actual=hashlib.sha256(ast.get_source_segment(src,node).encode()).hexdigest()
    if actual!=digest: fail(f'protected body changed {cls}.{fn}: {actual}')

# Execute H82 with tiny stubs. No Qt rendering is needed to prove cadence/dedup/authority policy.
logs=[]; scheduled=[]
class Qt: PreciseTimer=1
class H74PreviewStage:
    def __init__(self,*a,**kw): pass
    def _draw_text(self,*a,**kw): pass
    def _draw_per_char(self,*a,**kw): pass
class LyricWindow:
    def _actually_start(self,*a,**kw): self.base_start_calls=getattr(self,'base_start_calls',0)+1; return 'base-start'
class ControlPanel:
    def _resolve_qq_auto_track_duration_after_bind(self,job,cancel_check=None):
        self.base_resolver_calls=getattr(self,'base_resolver_calls',0)+1; return 0
class FakeTimer: pass
class Screen:
    def refreshRate(self): return 59.0
class PanelForHz:
    def screen(self): return Screen()
class QApplication:
    @staticmethod
    def primaryScreen(): return Screen()

def _h61_row_cache_init(w):
    if not hasattr(w,'_h61_row_atlas_queue'): w._h61_row_atlas_queue=[]
def _h61_row_key(w,text): return ('style-A',str(text))
def _h61_schedule_row_atlas(w,text): scheduled.append(str(text)); return 'scheduled'
def _h81_duration_conflict(a,b):
    a=int(a or 0); b=int(b or 0); tol=max(3500,int(max(a,b)*0.025)); return abs(a-b)>tol

def write_error_log(msg,*a,**kw): logs.append((msg,kw.get('detail','')))
def _h79_refresh_preview_rate(panel): return None
def _h69_prewarm_future_rows(window,anchor_index=None): return -1
H69_FUTURE_ROW_PREWARM=12; H81_DURATION_MIN_MS=30000
ns=globals().copy()
exec(compile(block,'<h82>','exec'),ns,ns)
if ns['_h82_preview_frame_interval'](PanelForHz()) != 17:
    fail('59 Hz preview cadence is not 17 ms')

class W(LyricWindow):
    def __init__(self):
        self._song_fragment_atlas_performance_fused=True
        self.lyric_timeline=[(i*100,f'row-{i}') for i in range(20)]
        self.displayed_line_index=0
        self._h61_row_atlas_queue=[]
w=W(); scheduled.clear()
first=ns['_h69_prewarm_future_rows'](w,0)
second=ns['_h69_prewarm_future_rows'](w,0)
third=ns['_h69_prewarm_future_rows'](w,1)
if (first,second,third)!=(12,0,1): fail(f'prewarm dedup mismatch {(first,second,third)}')
if len(scheduled)!=13: fail(f'expected 13 unique prewarm attempts, got {len(scheduled)}')
# A concrete new timeline clears stale queued prewarm without cancelling the one active worker.
w._h61_row_atlas_queue=[('old-key','old-text','old-style')]
w.lyric_timeline=list(w.lyric_timeline)
ns['_h69_prewarm_future_rows'](w,0)
if any(item and item[0]=='old-key' for item in w._h61_row_atlas_queue): fail('old timeline queue survived epoch change')
# New lyric session wrapper clears stale queued work before the base start.
w._h61_row_atlas_queue=[('stale','stale','style')]
result=w._actually_start('lyrics')
if result!='base-start' or w._h61_row_atlas_queue: fail('new lyric session did not clear stale prewarm queue')

class Choice:
    def currentText(self): return 'QQ音乐'
class Reader:
    def poll(self,*a,**kw): return {'source':'qq-time-pair-candidate','confidence':108,'duration_ms':239000,'position_ms':31000}
class Sync:
    def __init__(self): self._uia_reader=Reader()
    def snapshot(self): return {'media_title':'熱異常 (feat. 足立レイ)','media_artist':'いよわ','media_source':'QQMusic.exe'}
    def _source_matches_process_hint(self,source,proc): return 'qqmusic' in str(source).lower()
class P(ControlPanel):
    def __init__(self): self.player_combo=Choice(); self.media_sync=Sync(); self.base_resolver_calls=0
    def _same_track(self,*a): return True
p=P()
job={'source':'QQ音乐','song':'熱異常 (feat. 足立レイ)','artist':'いよわ','startup_existing_attach':True,
     'qq_prebind_duration_source':'qq-time-pair-candidate','qq_prebind_duration_ms':239000}
resolved=p._resolve_qq_auto_track_duration_after_bind(job)
if resolved!=239000: fail(f'startup-existing 239s witness not recovered: {resolved}')
if p.base_resolver_calls!=1: fail('H81/base resolver must remain first authority path')
job['startup_existing_attach']=False
if p._resolve_qq_auto_track_duration_after_bind(job)!=0: fail('normal track switch incorrectly reused prebind duration')

note=root/'RENDER_WORK_CONSOLIDATION_H82_NOTE_20260905.md'
if not note.is_file(): fail('missing H82 note')
print('RENDER WORK CONSOLIDATION H82 REPLAY: PASS')
print('  59 Hz motion preview uses precise ~17 ms cadence and cached vector outlines')
print('  future row/style prewarm is once-per-timeline instead of eviction-driven rebuild loop')
print('  stale queued row work is dropped on timeline/new lyric session boundaries')
print('  first attach to an already-running QQ track may reuse corroborated duration for lyric version only')
print('  normal QQ track-switch epoch isolation and protected transport/exit bodies remain unchanged')
