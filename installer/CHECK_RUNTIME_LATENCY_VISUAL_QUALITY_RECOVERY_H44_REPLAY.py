from pathlib import Path
import ast, sys, time, threading
from collections import OrderedDict

if len(sys.argv)!=2: raise SystemExit(2)
source=Path(sys.argv[1]); text=source.read_text(encoding='utf-8')

def need(c,m):
    if not c:
        print('RUNTIME LATENCY + VISUAL QUALITY RECOVERY H44 REPLAY: FAIL')
        print(' - '+m); raise SystemExit(1)

for m in [
    '+ RUNTIME LATENCY + VISUAL QUALITY RECOVERY H44',
    'H44酷狗新曲展示时钟立即解除卡死',
    'H44酷狗HostV2首个正样本快速校准展示',
    'H44网易云新身份阻止旧Payload版本重搜',
    'H44网易云过期异步歌词结果拒绝',
    'H44网易云错误版本重搜保持退避',
    'Atlas构建熔断仅停预计算',
]: need(m in text,'missing marker '+m)

need('_LIMBUS_H44_RENDER_ACTIVE_PRE' not in text,'H44 visual wrapper was not removed')
need('_LIMBUS_H44_RENDER_ARM_PRE' not in text,'H44 render-arm wrapper was not removed')
need('_LIMBUS_H44_AUTO_RESULT_PRE' not in text,'H44 auto-result wrapper was not removed')
need('_LIMBUS_H44_NCM_REQUEUE_PRE' not in text,'H44 NetEase requeue wrapper was not removed')
need('_LIMBUS_H44_KUGOU_COLD_PRE' not in text,'H44 KuGou cold-probe wrapper was not removed')
need('_LIMBUS_H44_KUGOU_PROGRESS_PRE' not in text,'H44 KuGou progress wrapper was not removed')
need('def _h44_activate_runtime' not in text,'empty H44 runtime activator was not removed')

tree=ast.parse(text)
wanted_assign={
    'H43_KUGOU_FIRST_HOST_DISPLAY_MIN_MS','H43_KUGOU_FIRST_HOST_DISPLAY_MAX_MS','H43_KUGOU_INSTRUMENTAL_SEED_LOG_MS',
    'H44_KUGOU_NEW_TRACK_DISPLAY_WINDOW_MS','H44_KUGOU_HOST_DISPLAY_MIN_MS','H44_NETEASE_RECONCILE_DEBOUNCE_SEC',
}
wanted_funcs={
    '_limbus_restore_visual_timer_cadence','_limbus_render_emergency_active','_limbus_arm_render_emergency',
    '_h38_ncm_current_identity','_h38_purge_conflicting_ncm_cache','_h38_requeue_version_reconcile',
    '_h41_auto_result','_h43_kugou_progress','_h43_kugou_cold_probe',
}
nodes=[]
for n in ast.walk(tree):
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in wanted_assign for t in n.targets): nodes.append(n)
    elif isinstance(n,ast.FunctionDef) and n.name in wanted_funcs: nodes.append(n)
nodes.sort(key=lambda n:n.lineno)

logs=[]
def write_error_log(*a,**k): logs.append((a,k))
def _clean_name(s): return ''.join(ch.lower() for ch in str(s or '') if ch.isalnum())
def _h38_duration_conflict(a,b):
    a=int(a or 0); b=int(b or 0)
    return a>=5000 and b>=5000 and abs(a-b)>max(1800,int(max(a,b)*0.025))
def _h42_kugou_frozen_safe(sync=None): return True

class UIReader:
    def set_startup_late_attach(self,v): self.late=bool(v)
class MediaSessionSync:
    def __init__(self):
        now=time.monotonic()*1000.0
        self._track_key='arustydream|doudou'; self._track_bound_mono=now-300.0
        self._media_player_epoch=2; self._track_identity_player_epoch=2
        self._startup_existing_attach=False; self._kugou_rail_master_active=False
        self._kugou_rail_master_position_ms=0.0; self._kugou_rail_master_status='unknown'
        self._h43_kugou_instrumental_presentation=False; self._uia_reader=UIReader()
        self._kugou_host_v2_progress_pending=None
        self._h38_ncm_player_duration_epoch=2; self._h38_ncm_player_duration_ms=196407
        self._h38_ncm_player_title='给陌生的你听'; self._h38_ncm_player_artist='张三'
    def _kugou_seed_rail_local_master(self,pos,status='unknown',reason='bootstrap',absolute=False,now_ms=None):
        self.seed=(float(pos),str(status),str(reason),bool(absolute)); self._kugou_rail_master_active=True
        self._kugou_rail_master_position_ms=float(pos); self._kugou_rail_master_status=str(status); return True
    def _kugou_rail_local_position(self,status='unknown'): return self._kugou_rail_master_position_ms if self._kugou_rail_master_active else None
    def _kugou_cold_bootstrap_transport_probe(self,status,fallback_position_ms=None): return False
    def _kugou_poll_uia_progress_v2(self,status='unknown',local_position_hint=None):
        self._kugou_host_v2_progress_pending={'source_key':'uia-range:Slider:::(0,0,1000,12)','last':1870.0,'count':1}; return None

class Combo:
    def __init__(self,v): self.v=v
    def currentText(self): return self.v
class Toggle:
    def __init__(self,v): self.v=bool(v)
    def isChecked(self): return self.v
class ControlPanel:
    def __init__(self):
        self.media_sync=MediaSessionSync(); self.player_combo=Combo('网易云音乐'); self.source_combo=Combo('网易云')
        self._is_started=True; self._auto_armed=True; self.auto_track_check=Toggle(True)
        self.trans_check=Toggle(False); self.precise_tracking_check=Toggle(True)
        self._auto_generation=1; self._auto_target_key=''; self.jobs=[]
        self._auto_lyric_cache_lock=threading.Lock(); self._auto_lyric_cache=OrderedDict(); self._auto_lyric_cache_limit=64
        self._h38_version_reconcile_sig='网易云音乐|网易云|旧歌|196'; self._h38_version_reconcile_mono=time.monotonic()
    def _same_track(self,a,b,c,d): return _clean_name(a)==_clean_name(c)
    def _track_identity(self,song,artist): return _clean_name(song)+'|'+_clean_name(artist)
    def _persist_auto_lyric_cache(self): self.persisted=True
    def _start_auto_search_job(self,job): self.jobs.append(dict(job))
    def _on_auto_lyric_result(self,row): self.base_rows=getattr(self,'base_rows',0)+1; self._h38_version_reconcile_sig=''; return True

class Timer:
    def __init__(self,i=16): self.i=i
    def isActive(self): return True
    def interval(self): return self.i
    def setInterval(self,v): self.i=int(v)
class LyricWindow:
    def __init__(self):
        self._song_fragment_atlas_fuse_reason='build-budget>850ms'; self._song_fragment_atlas_inflight=set()
        self._limbus_render_emergency_fused=True; self._limbus_render_emergency_reason='build-budget>850ms'
        self.line_timer=Timer(); self.fade_timer=Timer(); self.seek_entry_timer=Timer(); self.audio_emphasis_timer=Timer()
    def _animation_frame_interval(self): return 12

def old_active(window): return bool(getattr(window,'_limbus_render_emergency_fused',False) or getattr(window,'_song_fragment_atlas_performance_fused',False))
def old_arm(window,reason,elapsed_ms=0.0): window._limbus_render_emergency_fused=True; window._limbus_render_emergency_reason=str(reason); return None

ns=dict(MediaSessionSync=MediaSessionSync,ControlPanel=ControlPanel,LyricWindow=LyricWindow,time=time,threading=threading,OrderedDict=OrderedDict,
        write_error_log=write_error_log,_clean_name=_clean_name,_h38_duration_conflict=_h38_duration_conflict,
        _h42_kugou_frozen_safe=_h42_kugou_frozen_safe,
        _LIMBUS_H41_AUTO_RESULT_PRE=ControlPanel._on_auto_lyric_result,
        _LIMBUS_H43_PROGRESS_PRE=MediaSessionSync._kugou_poll_uia_progress_v2,
        _LIMBUS_H43_COLD_PRE=MediaSessionSync._kugou_cold_bootstrap_transport_probe,
        _limbus_render_emergency_active=old_active,_limbus_arm_render_emergency=old_arm,
        H43_KUGOU_FIRST_HOST_DISPLAY_MAX_MS=3600000.0)
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),ns)
ControlPanel._on_auto_lyric_result=ns['_h41_auto_result']
MediaSessionSync._kugou_poll_uia_progress_v2=ns['_h43_kugou_progress']
MediaSessionSync._kugou_cold_bootstrap_transport_probe=ns['_h43_kugou_cold_probe']

# Ordinary newly-started KuGou track must not wait tens of seconds for Host proof.
s=MediaSessionSync()
need(MediaSessionSync._kugou_cold_bootstrap_transport_probe(s,'playing',None) is True,'new ordinary KuGou track did not receive immediate display clock')
need(s.seed[0]==0.0 and s.seed[2]=='h44-new-track-presentation-local' and s.seed[3] is False,'new-track display clock gained absolute authority')

# Startup late-attach remains protected from synthetic zero.
s2=MediaSessionSync(); s2._startup_existing_attach=True
need(MediaSessionSync._kugou_cold_bootstrap_transport_probe(s2,'playing',None) is False and not s2._kugou_rail_master_active,'startup late-attach reopened synthetic zero')

# First positive Host Slider at 1.87s must calibrate display immediately, display-only.
s3=MediaSessionSync(); s3._startup_existing_attach=True
out=MediaSessionSync._kugou_poll_uia_progress_v2(s3,'playing',None)
need(out==1870 and s3._kugou_rail_master_active,'1.87s first Host sample still waited for later proof')
need(s3.seed[2]=='h44-host-first-positive-display' and s3.seed[3] is False,'Host first positive sample gained absolute/seek authority')

# Exact Host zero must not be accepted.
ns['_LIMBUS_H43_PROGRESS_PRE']=lambda sync,status='unknown',local_position_hint=None: (setattr(sync,'_kugou_host_v2_progress_pending',{'source_key':'uia-range:Slider:::(0,0,1000,12)','last':0.0,'count':1}) or None)
s4=MediaSessionSync(); s4._startup_existing_attach=True
out=MediaSessionSync._kugou_poll_uia_progress_v2(s4,'playing',None)
need(out is None and not s4._kugou_rail_master_active,'Host zero bypassed H42 zero quarantine')

# NetEase new native identity must veto old-payload version reconcile.
p=ControlPanel()
ret=ns['_h38_requeue_version_reconcile'](p,'酸橙色信笺','old',196407,'netease-native-duration')
need(ret is False and not p.jobs,'new native identity still drove old payload duration-refetch')

# Same identity may reconcile, but incompatible cached NCM payload must be evicted first.
p2=ControlPanel(); p2.media_sync._h38_ncm_player_title='给陌生的你听'; p2.media_sync._h38_ncm_player_artist='张三'
key=('网易云',False,True,_clean_name('给陌生的你听')+'|'+_clean_name('张三'),_clean_name('张三'),0)
p2._auto_lyric_cache[key]={'duration':229500,'lyric':'old'}
ret=ns['_h38_requeue_version_reconcile'](p2,'给陌生的你听','张三',196407,'netease-native-duration')
need(ret is True and len(p2.jobs)==1,'same-identity duration reconcile was incorrectly blocked')
need(key not in p2._auto_lyric_cache,'conflicting NCM cache survived duration-anchored reconcile')

# Async result for superseded identity must never reach historical display handler.
p3=ControlPanel()
out=ControlPanel._on_auto_lyric_result(p3,{'lyric':'x','song':'酸橙色信笺','artist':'old','duration':229500})
need(out is None and getattr(p3,'base_rows',0)==0,'stale NetEase result still updated display')

# Same-identity wrong version may be accepted by old handler, but H38 debounce must survive.
p4=ControlPanel(); p4.media_sync._h38_ncm_player_title='给陌生的你听'; p4.media_sync._h38_ncm_player_artist='张三'; pre=p4._h38_version_reconcile_sig
ControlPanel._on_auto_lyric_result(p4,{'lyric':'x','song':'给陌生的你听','artist':'张三','duration':229500})
need(p4._h38_version_reconcile_sig==pre and p4._h38_version_reconcile_sig,'H41 still erased H38 debounce after wrong-version refetch')

# Worker-only atlas build fuse must not permanently remove glow/cadence; hard paint still does.
w=LyricWindow(); w._song_fragment_atlas_performance_fused=True
need(ns['_limbus_render_emergency_active'](w) is False,'worker build-budget fuse still forced permanent plain-glyph renderer')
need(w.line_timer.interval()==12 and w.fade_timer.interval()==12,'visual cadence was not restored after worker-only fuse')
ns['_limbus_arm_render_emergency'](w,'build-budget>850ms',900)
need(not w._limbus_render_emergency_fused,'worker build fuse re-armed permanent emergency renderer')
ns['_limbus_arm_render_emergency'](w,'paint-hard-budget',180)
need(w._limbus_render_emergency_fused and ns['_limbus_render_emergency_active'](w) is True,'real slow paint no longer fails closed')

print('RUNTIME LATENCY + VISUAL QUALITY RECOVERY H44 REPLAY: PASS')
print(' - new KuGou tracks get an immediate display-only clock while startup late-attach zero stays forbidden')
print(' - first positive HostV2 Slider sample calibrates display without granting seek/duration authority')
print(' - NetEase new identity vetoes old-payload refetch; stale cache/results and debounce churn are closed')
print(' - worker-only atlas fuse keeps normal glow/cadence; true GUI paint overload still uses emergency renderer')
