from pathlib import Path
import ast, sys, time, types

if len(sys.argv) != 2:
    raise SystemExit(2)
source_path=Path(sys.argv[1]); text=source_path.read_text(encoding='utf-8')

def need(cond,msg):
    if not cond:
        print('MULTI-PROVIDER STATE AUTHORITY + LYRIC COMPLETENESS H41 REPLAY: FAIL')
        print(' - '+msg); raise SystemExit(1)

markers=[
    '+ MULTI-PROVIDER STATE AUTHORITY + LYRIC COMPLETENESS H41',
    'H41 QQ UNKNOWN运动证据接管展示',
    'H41 QQ跨播放器首锚使用现有播放器位置',
    'H41网易云版本重搜接受元数据即时提交',
    'H41酷狗Win10未授权视觉Rail禁止绝对时钟',
    'H41酷狗Win10新鲜GSMTC身份阻止Host回摆',
    'H41模式切换保持播放器时钟纪元',
    'H41跨源逐字歌词完整性拒绝',
    'H41跨源完整歌词恢复命中',
]
for m in markers: need(m in text,'missing H41 marker: '+m)

tree=ast.parse(text)
wanted_assign={n for n in [
'H41_QQ_UNKNOWN_MOTION_MIN_STREAK','H41_QQ_UNKNOWN_MOTION_MAX_AGE_MS','H41_QQ_UNKNOWN_MOTION_MAX_PACE_EXTRA_MS','H41_QQ_UNKNOWN_MOTION_MIN_STEP_MS','H41_QQ_CROSS_PLAYER_SEED_MIN_MS','H41_KUGOU_GSMTC_HOST_VETO_MS','H41_KUGOU_UNOWNED_VISUAL_LOG_MS','H41_KUGOU_FRAGMENT_HISTORY_TTL_MS','H41_KUGOU_FRAGMENT_HISTORY_MIN','H41_KUGOU_FRAGMENT_HISTORY_REL_SPREAD','H41_LYRIC_COMPLETENESS_MIN_DURATION_MS','H41_LYRIC_COMPLETENESS_MAX_TINY_EVENTS','H41_LYRIC_COMPLETENESS_MIN_LAST_MS','H41_LYRIC_COMPLETENESS_MIN_COVERAGE']}
wanted_funcs={'_h41_lrc_timestamps_ms','_h41_lyric_completeness','_h41_qq_unknown_motion_step','_h41_kugou_fragment_history_consensus','_h41_activate_runtime'}
nodes=[]
for node in tree.body:
    if isinstance(node,ast.Assign):
        if {t.id for t in node.targets if isinstance(t,ast.Name)} & wanted_assign: nodes.append(node)
    elif isinstance(node,ast.FunctionDef) and node.name in wanted_funcs: nodes.append(node)

# Pure QQ motion classifier: UNKNOWN + moving raw timeline becomes presentation evidence,
# while an isolated first sample and a backward discontinuity do not.
ns={'time':time}
exec(compile(ast.Module(body=[n for n in nodes if not (isinstance(n,ast.FunctionDef) and n.name=='_h41_activate_runtime')],type_ignores=[]),str(source_path),'exec'),ns)
ns['H38_KUGOU_VISUAL_DURATION_MIN_MS']=30000.0
ns['H38_KUGOU_VISUAL_DURATION_MAX_MS']=1800000.0
step=ns['_h41_qq_unknown_motion_step']
wall=1788180485000.0
st,p,tr=step({},630,wall,221626,1000,wall,1.0,'少女a|x'); need(not tr,'first UNKNOWN sample became trusted')
st,p,tr=step(st,1240,wall+610,221626,1610,wall+610,1.0,'少女a|x'); need(not tr,'one moving step became trusted too early')
st,p,tr=step(st,1840,wall+1210,221626,2210,wall+1210,1.0,'少女a|x'); need(tr and p>=1800,'coherent UNKNOWN motion did not become presentation evidence')
st2,p2,tr2=step(st,200,wall+1810,221626,2810,wall+1810,1.0,'少女a|x'); need(not tr2,'large backward UNKNOWN discontinuity retained motion trust')

# fake town baby regression: a 263s precise payload ending around 5s with six events is invalid,
# while a full-song sparse-but-real timeline remains valid.
bad='\n'.join(f'[00:0{i}.00]x' for i in range(6))
a=ns['_h41_lyric_completeness'](bad,263067)
need(a['bad'] and a['events']==6 and a['last_ms']<6000,'263s/6-event truncated payload was not rejected')
good='\n'.join(f'[{(i*3)//60:02d}:{(i*3)%60:02d}.00]line{i}' for i in range(88))
g=ns['_h41_lyric_completeness'](good,263067)
need(not g['bad'] and g['events']>=80 and g['coverage']>0.9,'complete long-song payload was rejected')

# Persistent KuGou fragment history may converge across visual-state resets/user gestures.
cons=ns['_h41_kugou_fragment_history_consensus'](221000,[
    {'duration':241700,'mono':1000,'ratio':0.20},
    {'duration':242400,'mono':2200,'ratio':0.31},
    {'duration':242050,'mono':3700,'ratio':0.44},
],4000)
need(cons is not None and abs(float(cons['duration_ms'])-242050)<1000,'cross-reset KuGou fragment history did not converge')

# Full runtime stubs for authority wrappers.
class DummyReader:
    def set_expected_duration(self,d): self.expected=d
class MediaSessionSync:
    def __init__(self):
        self._process_hint='qqmusic'; self._track_key='old|artist'; self._track_identity_player_epoch=1; self._media_player_epoch=2
        self._state={'position_ms':37988,'duration_ms':242112,'status':'paused','source':'QQMusic.exe','media_title':'少女A','media_artist':'x','media_source':'QQMusic.exe','media_metadata_mono':time.monotonic()*1000}
        self._uia_reader=DummyReader(); self._uia_duration_ms=0
    def _process_stem(self,s): return str(s or '').lower().replace('.exe','')
    def _source_matches_process_hint(self,source,hint): return self._process_stem(source)==self._process_stem(hint)
    def _qq_direct_gsmtc_witness(self,*a,**k): return None,False
    def _qq_update_gsmtc_identity_guard(self,*a,**k): return False
    def _qq_apply_direct_gsmtc_seek_authority(self,*a,**k): self.seek_calls=getattr(self,'seek_calls',0)+1; return True
    def _qq_select_public_clock(self,*a,**k): return None,None
    def _estimate_position_ms(self,*a,**k): return 0
    def snapshot(self): return dict(self._state)
    def bind_track(self,song,artist='',duration_ms=0,auto_provisional=False,initial_position_ms=0,netease_track_id=None,startup_existing=False):
        self.bind_initial=initial_position_ms; self.bind_calls=getattr(self,'bind_calls',0)+1; self._track_key='new|artist'; self._track_identity_player_epoch=self._media_player_epoch; return True
    def _set_state(self,**kw): self._state.update(kw)
    def _kugou_seed_rail_local_master(self,*a,**kw): self.seed_calls=getattr(self,'seed_calls',0)+1; return True
    def _kugou_poll_visual_rail_anchor(self,*a,**kw): return False

class Check:
    def isChecked(self): return True
class Combo:
    def __init__(self,v): self.v=v
    def currentText(self): return self.v
class ControlPanel:
    def __init__(self):
        self.media_sync=MediaSessionSync(); self.player_combo=Combo('网易云音乐'); self.source_combo=Combo('网易云'); self.auto_track_check=Check(); self.trans_check=Check(); self.precise_tracking_check=Check()
        self._is_started=True; self._auto_armed=True; self._auto_generation=3; self._auto_target_key='k'; self._loaded_song='少女A'; self._loaded_artist='x'
    def _qq_transport_duration_evidence(self,*a,**k): return 0
    def _on_auto_lyric_result(self,row): self._auto_target_key=''; return True
    def _track_identity(self,s,a=''): return 'k'
    def _same_track(self,a,b,c,d): return str(a).lower()==str(c).lower()
    def _detected_player_track(self): return ('旧标题','old')
    def _on_mode_lyric_result(self,result):
        self.media_sync.bind_track(result.get('song',''),result.get('artist',''),result.get('duration',0)); return True

class LyricSearchEngine:
    last_error=''
    _meta={}
    @staticmethod
    def search(*a,**k): return bad,263000
    @staticmethod
    def search_kugou(*a,**k): LyricSearchEngine._meta={'source':'酷狗'}; return good,None,263000
    @staticmethod
    def search_qq(*a,**k): LyricSearchEngine._meta={'source':'QQ音乐'}; return bad,None,263000
    @staticmethod
    def search_netease(*a,**k): return None,None,0
    @staticmethod
    def last_provider_meta(): return dict(LyricSearchEngine._meta)
    @staticmethod
    def _set_provider_meta(**kw): LyricSearchEngine._meta=dict(kw)

def _h37_kugou_win10_safe(sync): return True
def _h38_kugou_owned_duration(sync): return int(getattr(sync,'owned',0) or 0)
def _h38_accept_kugou_player_duration(sync,duration_ms,source='x',position_ratio=None,now_ms=None): sync.owned=int(duration_ms); return True
def _h30_visual_state(sync,provider): return {'proofs':[]}
def _provider_payload_instrumental(*a,**k): return False
def _lyric_clock_quality(text): return 3 if len(ns['_h41_lrc_timestamps_ms'](text))>=5 else 1
def write_error_log(*a,**k): pass
H38_KUGOU_VISUAL_DURATION_MIN_MS=30000.0; H38_KUGOU_VISUAL_DURATION_MAX_MS=1800000.0
runtime=dict(ns,MediaSessionSync=MediaSessionSync,ControlPanel=ControlPanel,LyricSearchEngine=LyricSearchEngine,
             _h37_kugou_win10_safe=_h37_kugou_win10_safe,_h38_kugou_owned_duration=_h38_kugou_owned_duration,
             _h38_accept_kugou_player_duration=_h38_accept_kugou_player_duration,_h30_visual_state=_h30_visual_state,
             _provider_payload_instrumental=_provider_payload_instrumental,_lyric_clock_quality=_lyric_clock_quality,
             write_error_log=write_error_log,H38_KUGOU_VISUAL_DURATION_MIN_MS=H38_KUGOU_VISUAL_DURATION_MIN_MS,
             H38_KUGOU_VISUAL_DURATION_MAX_MS=H38_KUGOU_VISUAL_DURATION_MAX_MS)
act=[n for n in nodes if isinstance(n,ast.FunctionDef) and n.name=='_h41_activate_runtime'][0]
exec(compile(ast.Module(body=[act],type_ignores=[]),str(source_path),'exec'),runtime)
runtime['_h41_activate_runtime']()

# Cross-player first QQ bind must seed from the existing player-owned 37.988s position.
s=MediaSessionSync(); MediaSessionSync.bind_track(s,'少女A','x',0,auto_provisional=True,initial_position_ms=78,startup_existing=False)
need(int(getattr(s,'bind_initial',0))==37988,'cross-player QQ bind still used metadata-age fake zero instead of player position')

# UNKNOWN motion may never acquire formal Seek authority.
s._h41_qq_unknown_motion_trusted=True
need(MediaSessionSync._qq_apply_direct_gsmtc_seek_authority(s,50000,'unknown') is False and getattr(s,'seek_calls',0)==0,
     'UNKNOWN motion reached formal QQ Seek authority')

# Semantic mode refetch must not call the old bind/reset path.
p=ControlPanel(); p.media_sync._track_key='少女a|鏡音リン'; before=getattr(p.media_sync,'bind_calls',0)
ControlPanel._on_mode_lyric_result(p,{'song':'少女A','artist':'鏡音リン、椎名もた','duration':221000})
need(getattr(p.media_sync,'bind_calls',0)==before,'mode switch still created a new media clock epoch')
need(int(p.media_sync._state.get('duration_ms') or 0)==221000,'mode switch in-place duration refresh failed')

# NetEase accepted result metadata must be committed using the pre-handler transaction state.
p=ControlPanel(); p._auto_target_key='k'; p.trans_check=types.SimpleNamespace(isChecked=lambda: True)
ControlPanel._on_auto_lyric_result(p,{'generation':3,'key':'k','source':'网易云','trans_only':True,'lyric':'[00:01]x','duration':230963,'song':'少女A','artist':'x'})
need(int(getattr(p,'_h38_loaded_candidate_duration_ms',0) or 0)==230963,'NetEase accepted payload metadata was still lost after historical handler cleanup')

# KuGou visual auto-anchor may not create an absolute clock before player duration is owned.
s=MediaSessionSync(); s._process_hint='kgmusic'; s.owned=0
need(MediaSessionSync._kugou_seed_rail_local_master(s,90000,status='playing',reason='visual-rail-auto',absolute=True) is False,
     'unowned KuGou visual-rail-auto still created absolute clock')
need(getattr(s,'seed_calls',0)==0,'blocked KuGou visual authority fell through to legacy seed')

# A fresh process-affine GSMTC identity already owning presentation vetoes a stale Host title.
pk=ControlPanel(); pk.player_combo=Combo('酷狗音乐'); pk._loaded_song='remix'; pk._loaded_artist='new'; pk.media_sync._process_hint='kgmusic'
pk.media_sync._state.update({'media_title':'remix','media_artist':'new','media_source':'kgmusic.exe','media_metadata_mono':time.monotonic()*1000.0})
host=ControlPanel._detected_player_track(pk)
need(host[0]=='remix','fresh KuGou GSMTC identity did not veto stale Host-V2 rollback')
s.owned=230000
need(MediaSessionSync._kugou_seed_rail_local_master(s,90000,status='playing',reason='visual-rail-auto',absolute=True) is True,
     'owned KuGou visual clock was incorrectly blocked')

# End-to-end completeness recovery should replace the six-event payload with the complete KRC candidate.
lyr,dur=LyricSearchEngine.search('fake town baby','UNISON SQUARE GARDEN','网易云',False,provider_duration_ms=263067,prefer_precise=True)
need(len(ns['_h41_lrc_timestamps_ms'](lyr))>=80 and dur==263000,'fake town baby completeness fallback did not choose the complete alternate payload')
need(LyricSearchEngine.last_provider_meta().get('h41_completeness_recovery') is True,'completeness recovery metadata not published')

print('MULTI-PROVIDER STATE AUTHORITY + LYRIC COMPLETENESS H41 REPLAY: PASS')
print(' - Win10 QQ UNKNOWN moving GSMTC is presentation/duration evidence but never Seek authority')
print(' - cross-player QQ first bind uses an existing player-owned position instead of metadata-age zero')
print(' - semantic mode switches keep the current media clock epoch')
print(' - NetEase accepted duration metadata closes repeated H38 version refetch')
print(' - KuGou unowned visual rail cannot bypass player-duration authority')
print(' - truncated long-song precise payloads fall through to complete cross-provider candidates')
