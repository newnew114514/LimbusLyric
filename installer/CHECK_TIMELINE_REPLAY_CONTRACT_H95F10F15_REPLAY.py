#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, json, pathlib, sys, time
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_TIMELINE_REPLAY_CONTRACT_H95F10F15_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); root=p.parent; src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ TIMELINE REPLAY CONTRACT H95F10F15' in src,'F15 build tag missing')
marker='# H95F10F15 timeline replay + opt-in trace contract'; need(marker in src,'F15 marker missing')
fixture_path=root/'installer'/'replays'/'QQ_FAST_STALE_OLD_PRECISE_UPGRADE_H95F10F15.json'
need(fixture_path.is_file(),'standard timeline replay fixture missing')
fx=json.loads(fixture_path.read_text(encoding='utf-8')); need(fx.get('schema')==1,'fixture schema mismatch')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name in ('_h95f10f5_should_block_qq_old_restore','_h95f10f6_qq_duration_second_chance','_h95f10f8_choose_bilingual_pair','_h95f10f15_compact_render_state','_h95f10f15_trace_event','_h95f10f15_frame_plan','_h95f10f15_trace_start','_h95f10f15_trace_stop','_h95f10f15_trace_snapshot','_h95f10f15_activate'):
    need(name in funcs,'missing '+name)
def fs(n): return ast.get_source_segment(src,funcs[n]) or ''
# F15 itself is diagnostics/test contract only; no new player/provider/effect or paint authority.
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for bad in ('LyricWindow.paintEvent =','FadingLine.draw =','LyricSearchEngine.search =','MediaSessionSync.position =','MediaSessionSync.seek =','MediaSessionSync.bind_track =','threading.Thread','requests.','_render_song_atlas_glyph(','_h62_filter_shared_image(','QPainterPath'):
    need(bad not in block,'F15 crossed runtime authority '+bad)
for t in ('_h95f10f15_trace_enabled',"'render-state'",'H95F10F15_TRACE_MAX_EVENTS = 192',"lyric.get('words') or ()",'word_count',"globals()['_h95f10f9_frame_plan'] = _h95f10f15_frame_plan"):
    need(t in block,'trace contract invariant missing '+t)

# 1) Exact F5 rollback predicate against the fixture.
f5=copy.deepcopy(funcs['_h95f10f5_should_block_qq_old_restore']); f5.decorator_list=[]
ns={'time':time,'H95F10F5_QQ_IDENTITY_ROLLBACK_GUARD_MS':2600.0}
exec(compile(ast.fix_missing_locations(ast.Module(body=[f5],type_ignores=[])),'<f15-f5>','exec'),ns)
class Combo:
    def currentText(self): return 'QQ音乐'
class Panel:
    player_combo=Combo(); _auto_overlay_suspended=True
    _auto_target_key=fx['new_track']['key']; _loaded_track_key=fx['old_track']['key']; _qq_background_hint_key=fx['new_track']['key']; _qq_background_hint_log_mono=fx['fast_event_mono']
    def _track_identity(self,song,artist=''): return f'{str(song).replace(" ","").lower()}|{artist}'
panel=Panel(); pred=ns['_h95f10f5_should_block_qq_old_restore']
need(pred(panel,fx['old_track']['song'],fx['old_track']['artist'],now_mono=float(fx['stale_old_snapshot_mono'])) is bool(fx['expected']['stale_old_restore_blocked']),'fixture stale-old rollback result mismatch')
need(pred(panel,fx['old_track']['song'],fx['old_track']['artist'],now_mono=float(fx['genuine_return_mono'])) is (not bool(fx['expected']['genuine_return_restore_allowed'])),'fixture genuine return result mismatch')

# 2) Exact F6 candidate->validated duration strengthening against the same fixture.
f6=copy.deepcopy(funcs['_h95f10f6_qq_duration_second_chance']); f6.decorator_list=[]
class FakeTime:
    def __init__(self): self.t=100.0
    def monotonic(self): return self.t
    def sleep(self,sec): self.t+=float(sec)
class Reader:
    def __init__(self,rows): self.rows=list(rows); self.i=0
    def poll(self,_proc): r=self.rows[min(self.i,len(self.rows)-1)]; self.i+=1; return dict(r)
class Media:
    def __init__(self,rows): self._uia_reader=Reader(rows)
    def snapshot(self): return {}
    def _source_matches_process_hint(self,*a): return True
class P:
    def __init__(self,rows): self.media_sync=Media(rows)
    def _same_track(self,*a): return True
ft=FakeTime(); dns={'time':ft,'H95F10F6_QQ_DURATION_SECOND_CHANCE_MS':220.0,'H95F10F6_QQ_DURATION_SECOND_CHANCE_POLL_MS':55.0,'_qq_duration_replays_prebind':lambda cand,pre_uia,pre_transport,pre_source: bool(pre_uia and cand==pre_uia),'write_error_log':lambda *a,**k:None}
exec(compile(ast.fix_missing_locations(ast.Module(body=[f6],type_ignores=[])),'<f15-f6>','exec'),dns)
resolved=dns['_h95f10f6_qq_duration_second_chance'](P(fx['duration_evidence']),dict(fx['duration_job']))
need(int(resolved)==int(fx['expected']['resolved_duration_ms']),'fixture duration strengthening mismatch')

# 3) Exact F8 bilingual pair chooser: quality-3 first only for precise mode.
f8=copy.deepcopy(funcs['_h95f10f8_choose_bilingual_pair']); f8.decorator_list=[]
ens={'write_error_log':lambda *a,**k:None}
exec(compile(ast.fix_missing_locations(ast.Module(body=[f8],type_ignores=[])),'<f15-f8>','exec'),ens)
rows=list(fx['bilingual_candidates'])
need(ens['_h95f10f8_choose_bilingual_pair'](rows,'QQ音乐',True)['provider']==fx['expected']['precise_pair_provider'],'fixture precise pair priority mismatch')
need(ens['_h95f10f8_choose_bilingual_pair'](rows,'QQ音乐',False)['provider']==fx['expected']['fast_pair_provider'],'fixture fast pair priority mismatch')

# 4) Trace contract is opt-in and compact: full word payload is never retained in compact state.
nodes=[]
for name in ('_h95f10f15_compact_render_state','_h95f10f15_trace_event','_h95f10f15_trace_start','_h95f10f15_trace_stop','_h95f10f15_trace_snapshot'):
    n=copy.deepcopy(funcs[name]); n.decorator_list=[]; nodes.append(n)
class T:
    @staticmethod
    def monotonic(): return 123.0
tns={'time':T,'H95F10F15_TRACE_SCHEMA':1,'H95F10F15_TRACE_MAX_EVENTS':192}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<f15-trace>','exec'),tns)
class W: pass
w=W(); need(tns['_h95f10f15_trace_event'](w,'x',{'a':1}) is False,'trace recorded while disabled')
tns['_h95f10f15_trace_start'](w); compact=tns['_h95f10f15_compact_render_state']({'idx':2,'route':'mature','lyric_input':{'quality':3,'words':[1,2,3]},'translation':'译','next_line_index':3})
need(compact['word_count']==3 and 'words' not in compact,'compact state retained full word payload')
need(tns['_h95f10f15_trace_event'](w,'render-state',compact) is True,'enabled trace rejected event')
snap=tns['_h95f10f15_trace_snapshot'](w); need(len(snap['events'])==1 and snap['events'][0]['data']['word_count']==3,'trace snapshot contract mismatch')
print('TIMELINE REPLAY CONTRACT H95F10F15 REPLAY: PASS')
print('  one fixture replays stale-old rollback + duration strengthening + precise pair priority: PASS')
print('  fixture executes mature F5/F6/F8 helpers directly; second state machine=0: PASS')
print('  runtime trace is opt-in, state-change/compact, no full word payload: PASS')
print('  provider/clock/search/effect/paint ownership unchanged: PASS')
