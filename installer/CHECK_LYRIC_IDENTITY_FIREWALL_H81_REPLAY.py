from pathlib import Path
import ast, hashlib, sys, threading, time
if len(sys.argv)<2: raise SystemExit('usage: CHECK_LYRIC_IDENTITY_FIREWALL_H81_REPLAY.py <main.py>')
main=Path(sys.argv[1]); src=main.read_text(encoding='utf-8'); root=main.parent

def fail(msg): raise SystemExit('H81 FAIL: '+msg)
def need(tok,label=None):
    if tok not in src: fail('missing '+(label or tok))

need('+ LYRIC IDENTITY FIREWALL H81','build tag')
need('# H81 lyric identity firewall / cross-version cache quarantine','marker')
if not (src.rindex("if '_h80_activate_ui' in globals():") < src.rindex("if '_h81_activate_runtime' in globals():")):
    fail('H81 must activate after H80')
block=src[src.index('# H81 lyric identity firewall / cross-version cache quarantine'):]
# Scope the executable replay to H81 itself. Later presentation/provider layers are separately
# gated and must not become accidental dependencies of this frozen authority replay.
_next_marker = '# H94 Spotify lyric fallback' if '# H94 Spotify lyric fallback' in block else '# H82 render work consolidation'
if _next_marker in block:
    block = block[:block.index(_next_marker)]
else:
    block = block[:block.index('if __name__ == "__main__":')]
for tok in (
    'def _h81_purge_unsafe_provider_cache(panel, target_key=\'\', source_filter=None):',
    "source_filter or ('QQ音乐', '酷狗')",
    "key_sec <= 0 and not instrumental",
    '_h81_duration_conflict(key_sec * 1000, payload_duration)',
    'def _h81_qq_player_duration(panel, song=\'\', artist=\'\'):',
    "source != 'qq-time-pair-validated' or confidence < 160",
    "str(j.get('qq_prebind_duration_source') or '') == 'qq-track-switch-hint'",
    "j['provider_duration_ms'] = 0",
    "H81 QQ旧Hint时长不得跨曲继承",
    "H81跨播放器歌词源Transport撤权",
    "j['provider_track_id'] = ''",
    "str(panel.player_combo.currentText() or '') != 'QQ音乐'",
    "meta.get('lyric_candidate_duration_ms')",
    "row['duration'] = 0",
    "meta['h81_transport_duration_withheld'] = True",
    "_h38_requeue_version_reconcile(",
    "player in ('QQ音乐', 'Spotify')",
    "media-rebind=0",
):
    need(tok)
# H81 may coordinate ControlPanel boundaries, but must not replace source-locked player clocks.
for bad in (
    'MediaSessionSync._merge_uia_position =', 'MediaSessionSync.bind_track =',
    'AsyncPlayerUiPositionReader.poll =', 'LyricSearchEngine.search =',
    'FadingLine.update =', 'FadingLine.draw ='
):
    if bad in block: fail('crossed protected authority boundary: '+bad)

# H81 authority boundaries remain frozen. R2 intentionally revises only _merge_uia_position
# to let a strictly advancing QQ UIA stream prove *player duration* without lyric authority;
# this digest is the reviewed R2 body. R2.4 also intentionally consumes first-attach state in
# _request_auto_track; its reviewed body is locked below. Other protected historical bodies remain frozen.
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

# Execute only H81 with tiny stubs to replay the exact regression shape: 203s lyric arrives while
# QQ player duration is unknown, so duration must be withheld; once validated UIA says 239s, a
# duration-anchored refetch must be scheduled instead of poisoning MediaSync.
ns={'time':time,'threading':threading}
logs=[]; requeues=[]
ns['write_error_log']=lambda msg,*a,**kw: logs.append((msg,kw.get('detail','')))
class MediaSessionSync: pass
class ControlPanel:
    def _load_auto_lyric_cache_from_disk(self): return True
    def _start_auto_search_job(self,job): self.started_job=dict(job); return True
    def _resolve_qq_auto_track_duration_after_bind(self,job,cancel_check=None):
        self.qq_resolver_calls=int(getattr(self,'qq_resolver_calls',0) or 0)+1
        return 777000
    def _on_auto_lyric_result(self,row): self.accepted_row=dict(row); return True
    def _monitor_track_change(self): return True
ns.update({'ControlPanel':ControlPanel,'MediaSessionSync':MediaSessionSync})
ns['_h38_requeue_version_reconcile']=lambda panel,song,artist,duration,reason: requeues.append((song,artist,duration,reason)) or True
exec(compile(block,'<h81>', 'exec'),ns,ns)

class Choice:
    def __init__(self,v): self.v=v
    def currentText(self): return self.v
class Check:
    def __init__(self,v=True): self.v=v
    def isChecked(self): return self.v
class Reader:
    def __init__(self): self.mode='candidate'
    def poll(self,*a,**kw):
        if self.mode=='validated': return {'source':'qq-time-pair-validated','confidence':168,'duration_ms':239000}
        return {'source':'qq-time-pair-candidate','confidence':108,'duration_ms':239000}
class Sync:
    def __init__(self): self._uia_reader=Reader()
    def snapshot(self): return {'media_title':'熱異常 (feat. 足立レイ)','media_artist':'いよわ','media_source':'QQMusic.exe'}
    def _source_matches_process_hint(self,source,process): return 'qqmusic' in str(source).lower()
class LyricWindow: song_duration=0
class Panel(ControlPanel):
    def __init__(self):
        self.player_combo=Choice('QQ音乐'); self.source_combo=Choice('QQ音乐')
        self.auto_track_check=Check(); self.trans_check=Check(False)
        self._is_started=True; self._auto_armed=True; self._auto_generation=7
        self._auto_target_key='熱異常feat足立レイ|いよわ'; self._auto_lyric_cache={}; self._auto_lyric_cache_lock=threading.Lock()
        self.media_sync=Sync(); self.lyric_window=LyricWindow(); self._loaded_song='熱異常 (feat. 足立レイ)'; self._loaded_artist='いよわ'
        self.qq_resolver_calls=0
    def _track_identity(self,song,artist=''): return '熱異常feat足立レイ|いよわ'
    def _same_track(self,a,b,c,d): return self._track_identity(a,b)==self._track_identity(c,d)
    def _qq_transport_duration_evidence(self,*a,**kw): return 0
    def _persist_auto_lyric_cache(self): self.persisted=True
p=Panel()
# Bad persisted zero-duration precise row must be removed.
p._auto_lyric_cache[('QQ音乐',False,True,p._auto_target_key,'いよわ',0)]={'lyric':'bad','duration':203000,'provider_meta':{}}
p._load_auto_lyric_cache_from_disk()
if p._auto_lyric_cache: fail('unsafe QQ zero-duration cache survived load')
# A prebind hint must not short-circuit the post-bind resolver.
p._start_auto_search_job({'source':'QQ音乐','key':p._auto_target_key,'song':p._loaded_song,'artist':p._loaded_artist,
    'provider_duration_ms':239000,'qq_prebind_duration_ms':239000,'qq_prebind_duration_source':'qq-track-switch-hint'})
if int(p.started_job.get('provider_duration_ms') or 0)!=0: fail('prebind track-switch hint still owns provider duration')
# Unknown player duration: allow words but withhold 203s from MediaSync.
row={'generation':7,'key':p._auto_target_key,'source':'QQ音乐','trans_only':False,'song':p._loaded_song,'artist':p._loaded_artist,
     'lyric':'[00:01.00]bad','duration':203000,'provider_duration_ms':0,'provider_meta':{},'precision_upgrade':True}
p._on_auto_lyric_result(row)
if int(p.accepted_row.get('duration') or 0)!=0: fail('unverified 203s lyric duration reached base auto-result')
if int(getattr(p,'_h81_unverified_candidate_duration_ms',0) or 0)!=203000: fail('unverified duration was not quarantined')
# Later selected-player proof must refetch with 239s, not rebind the old 203s duration.
p.media_sync._uia_reader.mode='validated'; p._monitor_track_change()
if not requeues or requeues[-1][2]!=239000: fail('validated 239s player duration did not trigger refetch')
if int(getattr(p.lyric_window,'song_duration',0) or 0)!=0: fail('conflicting candidate restored presentation duration before refetch')

# Fast-stage payloads publish duration=0 but retain the provider candidate in metadata.  A failed
# precise upgrade must not hide that 203s version from the late 239s player reconciliation.
requeues.clear(); p=Panel()
fast_row={'generation':7,'key':p._auto_target_key,'source':'QQ音乐','trans_only':False,'song':p._loaded_song,'artist':p._loaded_artist,
          'lyric':'[00:01.00]fast-bad','duration':0,'provider_duration_ms':0,
          'provider_meta':{'progressive_fast_stage':True,'lyric_candidate_duration_ms':203000},
          'progressive_stage':'fast','precision_upgrade_pending':True,'precision_upgrade':False}
p._on_auto_lyric_result(fast_row)
if int(getattr(p,'_h81_unverified_candidate_duration_ms',0) or 0)!=203000:
    fail('fast-stage hidden candidate duration was not quarantined for late reconcile')
p.media_sync._uia_reader.mode='validated'; p._monitor_track_change()
if not requeues or requeues[-1][2]!=239000:
    fail('fast-stage hidden 203s candidate did not reconcile against validated 239s player duration')

# Equivalent cross-provider Spotify gap: while selected Spotify duration is not published yet,
# a QQ provider candidate must not become transport duration; once Spotify GSMTC appears it
# owns version selection and triggers the same duration-anchored reconcile.
requeues.clear(); p=Panel(); p.player_combo=Choice('Spotify'); p.source_combo=Choice('QQ音乐')
ns['_h13_spotify_duration_witness']=lambda panel,song='',artist='': int(getattr(panel,'spotify_witness',0) or 0)
p.spotify_witness=0
# A foreign NetEase lyric source may have captured a Bridge transport ID/duration from another
# running app.  H81 must remove both before the inner search path sees them.
p.source_combo=Choice('网易云')
p._start_auto_search_job({'source':'网易云','key':p._auto_target_key,'song':p._loaded_song,'artist':p._loaded_artist,
    'provider_duration_ms':203000,'provider_track_id':'foreign-ncm-id'})
if int(p.started_job.get('provider_duration_ms') or 0)!=0 or p.started_job.get('provider_track_id'):
    fail('foreign NetEase transport hint survived Spotify lyric-source boundary')
# A QQ lyric-source worker must also never poll QQ transport when Spotify owns playback.
p.source_combo=Choice('QQ音乐')
resolved=p._resolve_qq_auto_track_duration_after_bind({'song':p._loaded_song,'artist':p._loaded_artist})
if resolved!=0 or p.qq_resolver_calls!=0:
    fail('non-QQ selected player still invoked foreign QQ duration resolver')
p.spotify_witness=239000
resolved=p._resolve_qq_auto_track_duration_after_bind({'song':p._loaded_song,'artist':p._loaded_artist})
if resolved!=239000 or p.qq_resolver_calls!=0:
    fail('Spotify player-owned duration was not used instead of foreign QQ resolver')
# Restore zero witness for the lyric-result quarantine case below.
p.spotify_witness=0
row={'generation':7,'key':p._auto_target_key,'source':'QQ音乐','trans_only':False,'song':p._loaded_song,'artist':p._loaded_artist,
     'lyric':'[00:01.00]provider','duration':203000,'provider_duration_ms':0,'provider_meta':{},'precision_upgrade':True}
p._on_auto_lyric_result(row)
if int(p.accepted_row.get('duration') or 0)!=0: fail('Spotify zero-witness cross-provider duration reached MediaSync')
p.spotify_witness=239000; p._monitor_track_change()
if not requeues or requeues[-1][2]!=239000: fail('Spotify GSMTC witness did not own cross-provider version reconcile')

note=root/'LYRIC_IDENTITY_FIREWALL_H81_NOTE_20260905.md'
if not note.is_file(): fail('missing H81 note')
print('LYRIC IDENTITY FIREWALL H81 REPLAY: PASS')
print('  203s unknown-duration lyric cannot become QQ transport duration')
print('  validated 239s selected-player duration schedules duration-anchored refetch')
print('  QQ prebind track-switch hint no longer short-circuits new-track duration proof')
print('  fast-stage hidden candidate duration remains eligible for late player-duration reconcile')
print('  cross-player lyric sources cannot lend NetEase/QQ transport identity to another player')
print('  Spotify zero-witness cross-provider lyric duration is also transport-non-authoritative')
print('  R2-reviewed QQ merge body is locked; other H80 protected bodies remain frozen')
