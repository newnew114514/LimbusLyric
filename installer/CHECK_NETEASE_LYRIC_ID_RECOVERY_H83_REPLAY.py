"""Log-derived NetEase ID conflict recovery; real source functions, fake external services."""
import ast
import re
import sys
import threading
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace as NS

root = Path(sys.argv[1])
tree = ast.parse(next(root.glob('LimbusLyric_*.py')).read_text(encoding='utf-8'))
top = {n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
checks = []
def check(name, good):
    checks.append(bool(good)); print(('PASS ' if good else 'FAIL ')+name,flush=True)
def load(nodes, ns): exec(compile(ast.Module(body=nodes,type_ignores=[]),'<real-source>','exec'),ns)

key_node = next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='cache_key_for')
ns = dict(re=re,source='网易云',trans_only=False,job=dict(key='stringtheocracy|mili',artist='Mili',provider_track_id='1887467085'))
load([top['_clean_name'],key_node],ns)
a=ns['cache_key_for'](True,174170)
ns['job']['provider_track_id']='1452463974'
b=ns['cache_key_for'](True,174170)
check('same-title same-duration distinct IDs use distinct cache keys',a!=b)
ns['source']='QQ音乐'
check('QQ cache shape stays six fields',len(ns['cache_key_for'](True,174170))==6)

needed=('_h83_netease_player_hint','_h83_reconcile_netease_id','_h83_guard_netease_result')
if not all(n in top for n in needed):
    check('ID recovery path exists',False)
    raise SystemExit(1)
clock=NS(now=10.0)
jobs=[]
ns.update(time=NS(monotonic=lambda:clock.now,time=lambda:1700000000.0,sleep=lambda seconds:setattr(clock,'now',clock.now+float(seconds))),write_error_log=lambda *a,**kw:None)
load([top[n] for n in needed]+[top['_h45_netease_native_identity_ok']],ns)
clean=ns['_clean_name']
def panel(title='String Theocracy',bound='1887467085',native='1452463974'):
    raw=dict(ready=True,title=title,artist='Mili',track_id=native,duration_ms=174170,track_serial=1)
    sync=NS(_process_hint='cloudmusic',_media_player_epoch=1,_netease_bridge_bound_track_id=bound,
            _state={'player_liveness':'alive'},_track_key=clean(title)+'|mili',
            _netease_native=NS(snapshot=lambda:dict(raw)))
    p=NS(media_sync=sync,_loaded_song=title,_loaded_artist='Mili',_auto_fetch_in_progress=False,
         player_combo=NS(currentText=lambda:'网易云音乐'),source_combo=NS(currentText=lambda:'网易云'),
         _same_track=lambda s,a,t,b:clean(s)==clean(t) and clean(a)==clean(b),
         status=NS(setText=lambda value:None))
    return p,raw
def requeue(p,s,a,d,reason,provider_track_id=''):
    jobs.append(provider_track_id);p._auto_fetch_in_progress=True;return True
ns['_h38_requeue_version_reconcile']=requeue
recover=ns['_h83_reconcile_netease_id'];guard=ns['_h83_guard_netease_result']
p,raw=panel()
recover(p,p._loaded_song,'Mili')
check('one observation does not start refetch',not jobs)
clock.now+=1
recover(p,p._loaded_song,'Mili')
check('stable conflict refetches actual player ID',jobs==['1452463974'])
for _ in range(10): clock.now+=1;recover(p,p._loaded_song,'Mili')
check('in-flight recovery is not duplicated',len(jobs)==1)
for _ in range(10):
    p._auto_fetch_in_progress=False;clock.now+=31;recover(p,p._loaded_song,'Mili')
check('unresolved conflict has bounded retry count',len(jobs)==3)
check('retry exhaustion explains version mismatch',getattr(p,'_h83_sync_reason','')=='歌曲版本未匹配')
raw['ready']=False;recover(p,p._loaded_song,'Mili')
raw['ready']=True;clock.now+=31;recover(p,p._loaded_song,'Mili');clock.now+=1;recover(p,p._loaded_song,'Mili')
check('temporary native outage does not reset exhausted retry budget',len(jobs)==3)

def result(track_id):
    return dict(source='网易云',song=p._loaded_song,artist='Mili',provider_track_id=track_id,
                provider_meta={'netease_song_id':track_id},lyric='[00:01]test',precision_upgrade_pending=False)
wrong=result('1887467085');guard(p,wrong)
check('wrong cached/provider ID cannot be committed',wrong['lyric'] is None)
right=result('1452463974');guard(p,right)
check('correct exact-ID result can be committed',bool(right['lyric']))
p.media_sync._netease_bridge_bound_track_id=right['provider_meta']['netease_song_id']
ok,_=ns['_h45_netease_native_identity_ok'](p.media_sync,raw)
check('matching rebind restores existing native identity gate',ok)
recover(p,p._loaded_song,'Mili')
check('successful recovery clears waiting reason',not p._h83_sync_reason)
raw['track_id']='999';stale=result('1452463974');guard(p,stale)
check('same-title player ID change rejects late response',stale['lyric'] is None)
raw['title']='Other track';stale=result('1452463974');guard(p,stale)
check('different-title player change rejects late response',stale['lyric'] is None)

p,raw=panel('恋人を射ち堕とした日','22782041','22782085')
raw['artist']='Mili'
clock.now+=31;recover(p,p._loaded_song,'Mili');clock.now+=1;recover(p,p._loaded_song,'Mili')
check('second logged conflict uses actual ID',jobs[-1]=='22782085')
p,raw=panel();raw['ready']=False
check('unavailable native identity does not fabricate an ID',ns['_h83_netease_player_hint'](p) is None)
p,raw=panel();p.media_sync._state['player_liveness']='dead'
check('dead player cannot trigger native recovery',ns['_h83_netease_player_hint'](p) is None)

# Exercise the actual auto-result call site: old precise lyrics must not prevent
# an identity-correct ordinary result from reaching bind_track.
control=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ControlPanel')
methods={n.name:n for n in control.body if isinstance(n,ast.FunctionDef)}
load([methods['_on_auto_lyric_result']],ns)
ns['CLOCK_SOURCE_FIRST_ENABLED']=True
ns['_lyric_clock_quality']=lambda text:10 if text=='old precise' else 1
p,raw=panel()
p._is_started=p._auto_armed=True;p._auto_generation=5;p._auto_target_key='stringtheocracy|mili'
p.auto_track_check=NS(isChecked=lambda:True);p.trans_check=NS(isChecked=lambda:False)
p._loaded_source='网易云';p._active_lyric_provider_meta={'netease_song_id':'1887467085'}
p.lyric_window=NS(song_duration=174170)
texts=[];bound=[]
p.text_input=NS(toPlainText=lambda:'old precise',setPlainText=lambda value:texts.append(value))
class ReachedBind(Exception): pass
def bind(*a,**kw): bound.append(kw['netease_track_id']);raise ReachedBind()
p.media_sync.bind_track=bind
row=result('1452463974');row.update(generation=5,key=p._auto_target_key,duration=174170,precision_upgrade=True)
try: ns['_on_auto_lyric_result'](p,row)
except ReachedBind: pass
check('real callback replaces old-version precise payload',texts==['[00:01]test'])
check('real callback rebinds ID even for precision-upgrade result',bound==['1452463974'])

# Execute the real search worker synchronously; only external search/thread/signal are replaced.
load([methods['_start_auto_search_job']],ns)
emitted=[];queries=[]
class Thread:
    def __init__(self,target,**kw):self.target=target
    def start(self):self.target()
class Engine:
    last_error=''
    @staticmethod
    def _set_cancel_check(value):pass
    @staticmethod
    def search(*a,**kw):queries.append(kw.get('provider_track_id'));return '[00:01]correct',174170
    @staticmethod
    def last_provider_meta():return {'netease_song_id':'1452463974'}
ns['threading']=NS(Thread=Thread,Event=threading.Event)
ns['LyricSearchEngine']=Engine
p,raw=panel();p._auto_generation=5;p._auto_target_key='stringtheocracy|mili'
p._auto_lyric_cache_lock=threading.Lock();p._auto_lyric_cache_limit=24
p._auto_lyric_cache=OrderedDict({('网易云',False,False,p._auto_target_key,'mili',0):dict(lyric='old cached',duration=174170,provider_meta={'netease_song_id':'1887467085'})})
p._persist_auto_lyric_cache=lambda:None
p.auto_lyric_result=NS(emit=lambda value:emitted.append(value))
job=dict(generation=5,key=p._auto_target_key,song=p._loaded_song,artist='Mili',source='网易云',trans_only=False,prefer_precise=False)
ns['_start_auto_search_job'](p,job)
check('real worker bypasses old cache and searches native ID',queries==['1452463974'])
check('real worker returns identity-correct lyrics',len(emitted)==1 and emitted[0]['lyric']=='[00:01]correct')
Engine.last_provider_meta=staticmethod(lambda:{'netease_song_id':'1887467085'})
p._auto_lyric_cache.clear();emitted.clear()
ns['_start_auto_search_job'](p,job)
check('real worker rejects wrong-ID provider result',len(emitted)==1 and not emitted[0]['lyric'])
check('wrong-ID provider result is not cached',not p._auto_lyric_cache)
load([top['_h38_requeue_version_reconcile'],top['_h38_ncm_current_identity']],ns)
ns['_h38_purge_conflicting_ncm_cache']=lambda *a:0
p._is_started=p._auto_armed=True
p.auto_track_check=NS(isChecked=lambda:True);p.trans_check=NS(isChecked=lambda:False)
p._track_identity=lambda s,a:clean(s)+'|'+clean(a)
requeued=[];p._start_auto_search_job=lambda row:requeued.append(row)
started=ns['_h38_requeue_version_reconcile'](p,p._loaded_song,'Mili',174170,'native-track-id-conflict',provider_track_id='1452463974')
check('real reconciliation builder forwards exact ID and new generation',started and requeued[0]['provider_track_id']=='1452463974' and requeued[0]['generation']==6)
qq=dict(source='QQ音乐',lyric='qq unchanged',provider_meta={})
guard(p,qq)
check('NetEase result guard leaves QQ payload unchanged',qq['lyric']=='qq unchanged')
p.media_sync._process_hint='qqmusic'
check('player switch prevents stale native observation',ns['_h83_netease_player_hint'](p) is None)
p,raw=panel();p.media_sync._netease_bridge_primary=True
check('healthy Bridge keeps priority over native observation',ns['_h83_netease_player_hint'](p) is None)
p,raw=panel();raw['duration_ms']=float('inf')
check('invalid native duration cannot escape into GUI search setup',ns['_h83_netease_player_hint'](p) is None)
print(f'H83 NETEASE LYRIC ID RECOVERY: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
