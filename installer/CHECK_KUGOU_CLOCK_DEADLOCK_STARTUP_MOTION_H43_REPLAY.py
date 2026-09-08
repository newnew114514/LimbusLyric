from pathlib import Path
import ast, sys as _real_sys, types, time

if len(_real_sys.argv)!=2: raise SystemExit(2)
source=Path(_real_sys.argv[1]); text=source.read_text(encoding='utf-8')

def need(c,m):
    if not c:
        print('KUGOU CLOCK DEADLOCK + STARTUP MOTION H43 REPLAY: FAIL')
        print(' - '+m); raise SystemExit(1)
for m in [
    '+ KUGOU CLOCK DEADLOCK + STARTUP MOTION SAFETY H43',
    'H43酷狗纯音乐展示时钟解除卡死',
    'H43酷狗HostV2首个非零样本解除卡死',
    'H43 Windows frozen启动动画安全跳过',
    "_limbus_first_sample_policy='nonzero-slider-display-only'",
    "_limbus_instrumental_policy='status-only-display-no-seek-authority'",
]: need(m in text,'missing marker '+m)
need("if '_h42_windows_frozen' in globals() and _h42_windows_frozen():" in text,
     'frozen startup animation bypass missing')

tree=ast.parse(text)
wanted_assign={
    'H43_KUGOU_FIRST_HOST_DISPLAY_MIN_MS','H43_KUGOU_FIRST_HOST_DISPLAY_MAX_MS','H43_KUGOU_INSTRUMENTAL_SEED_LOG_MS',
    'H44_KUGOU_NEW_TRACK_DISPLAY_WINDOW_MS','H44_KUGOU_HOST_DISPLAY_MIN_MS',
}
wanted_funcs={'_h43_activate_runtime'}
nodes=[]
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in wanted_assign for t in n.targets): nodes.append(n)
    elif isinstance(n,ast.FunctionDef) and n.name in wanted_funcs: nodes.append(n)

logs=[]
def write_error_log(*a,**k): logs.append((a,k))
def _h42_kugou_frozen_safe(sync=None): return True
def _is_instrumental_boilerplate_payload(text): return '纯音乐' in str(text)
class TextBox:
    def __init__(self,t): self.t=t
    def toPlainText(self): return self.t
class Combo:
    def currentText(self): return '酷狗音乐'
class UIReader:
    def set_startup_late_attach(self,v): self.late=v
class MediaSessionSync:
    def __init__(self):
        self._process_hint='kgmusic.exe'; self._track_key='inst|artist'; self._media_player_epoch=3; self._track_identity_player_epoch=3
        self._kugou_rail_master_active=False; self._kugou_rail_master_position_ms=0.0; self._state={'status':'playing'}
        self._uia_reader=UIReader(); self._startup_existing_attach=True; self._kugou_host_v2_progress_pending=None
    def bind_track(self,song,artist='',duration_ms=0,auto_provisional=False,initial_position_ms=0,netease_track_id=None,startup_existing=False):
        self._track_key=(song+'|'+artist).lower(); return True
    def _kugou_seed_rail_local_master(self,pos,status='unknown',reason='bootstrap',absolute=False,now_ms=None):
        self.seed=(float(pos),status,reason,bool(absolute)); self._kugou_rail_master_active=True; self._kugou_rail_master_position_ms=float(pos); return True
    def _kugou_poll_uia_progress_v2(self,status,local_position_hint=None):
        # emulate base reader returning proof-pending None after first plausible native Slider sample
        self._kugou_host_v2_progress_pending={'source_key':'uia-range:Slider:::(0,0,1000,12)','last':122550.0,'count':1}
        return None
    def _kugou_cold_bootstrap_transport_probe(self,status,fallback_position_ms=None): return False
class ControlPanel:
    def __init__(self,sync,text='[00:00.00]纯音乐，请欣赏'):
        self.media_sync=sync; self.player_combo=Combo(); self.text_input=TextBox(text); self._active_lyric_provider_meta={}
    def _launch_current_lyrics(self,start_delay=0): self.launched=True; return True

ns=dict(MediaSessionSync=MediaSessionSync,ControlPanel=ControlPanel,time=time,write_error_log=write_error_log,
        _h42_kugou_frozen_safe=_h42_kugou_frozen_safe,_is_instrumental_boilerplate_payload=_is_instrumental_boilerplate_payload)
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),ns)
ns['_h43_activate_runtime']()

# Instrumental startup with PLAYING + no real clock gets a presentation-only monotonic seed.
s=MediaSessionSync(); p=ControlPanel(s)
need(p._launch_current_lyrics(start_delay=0) is True,'launch wrapper failed')
need(bool(getattr(s,'_h43_kugou_instrumental_presentation',False)),'instrumental presentation flag not armed')
need(s._kugou_cold_bootstrap_transport_probe('playing',None) is True,'instrumental no-clock cold probe stayed deadlocked')
need(s.seed[0]==0.0 and s.seed[2]=='h43-instrumental-presentation-local' and s.seed[3] is False,
     'instrumental clock gained wrong authority')

# Ordinary startup: first non-zero plausible Slider sample can seed display-only before formal proof.
s2=MediaSessionSync(); s2._h43_kugou_instrumental_presentation=False
out=s2._kugou_poll_uia_progress_v2('playing',None)
need(out==122550 and s2._kugou_rail_master_active,'first non-zero Host sample did not unlock display clock')
need(s2.seed[2]=='h43-host-first-sample-provisional' and s2.seed[3] is False,
     'first Host sample incorrectly gained absolute/seek authority')

# A zero Host sample may not bootstrap a mid-song startup attach.
s3=MediaSessionSync()
def zero_pre(status,local_position_hint=None):
    s3._kugou_host_v2_progress_pending={'source_key':'uia-range:Slider:::(0,0,1000,12)','last':0.0,'count':1}; return None
# replace captured pre used by H43 wrapper
ns['_LIMBUS_H43_PROGRESS_PRE']=lambda sync,status,local_position_hint=None: (setattr(sync,'_kugou_host_v2_progress_pending',{'source_key':'uia-range:Slider:::(0,0,1000,12)','last':0.0,'count':1}) or None)
s3._kugou_rail_master_active=False
out=ns['MediaSessionSync']._kugou_poll_uia_progress_v2(s3,'playing',None)
need(out is None and not s3._kugou_rail_master_active,'zero Host sample reopened synthetic-zero startup bug')

print('KUGOU CLOCK DEADLOCK + STARTUP MOTION H43 REPLAY: PASS')
print(' - instrumental PLAYING/no-clock startup receives presentation-only monotonic clock')
print(' - first non-zero plausible HostV2 Slider sample unlocks display before formal proof')
print(' - zero Host sample remains quarantined and neither path grants seek/duration authority')
print(' - frozen Windows startup animation is skipped at the repeated 0x8001010d stack site')
