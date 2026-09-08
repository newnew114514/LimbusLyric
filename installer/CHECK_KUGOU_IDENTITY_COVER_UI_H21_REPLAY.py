#!/usr/bin/env python3
from pathlib import Path
import threading, time, re

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
src=MAIN.read_text(encoding='utf-8')
h21='# H21 KuGou identity corroboration / cover-control placement'
h14='# H14 auto-precision deadline / bounded enhancement'
assert h21 in src and h14 in src and src.index(h21)<src.index(h14)
for needle in (
    "H21_KUGOU_HOST_IDENTITY_VETO_SEC = 3.0",
    "H21_KUGOU_HOST_HINT_WAIT_SEC = 0.55",
    "H21酷狗陈旧GSMTC身份否决",
    "H21酷狗精准版本证据晚到救援",
    "H21封面跟色控件归位",
    "target_layout.insertWidget(target_idx+1,self.h12_cover_check)",
    "config-key=h12_cover_follow",
):
    assert needle in src, needle

block=src[src.index(h21):src.index(h14)]
logs=[]
def write_error_log(label,*a,**kw): logs.append((label,kw.get('detail','')))
def clean(x): return re.sub(r'\W+','',str(x or '').casefold())

class FakeCombo:
    def __init__(self,text='酷狗音乐'): self.text=text
    def currentText(self): return self.text
class FakeCheck:
    def __init__(self): self.text=''; self.tip=''
    def setText(self,x): self.text=x
    def setToolTip(self,x): self.tip=x
class FakeLayout:
    def count(self): return 0
class FakeFetcher:
    old_calls=0
    @staticmethod
    def get_kugou_ui_duration_hint(pids,song_name,max_nodes=640):
        FakeFetcher.old_calls+=1
        return 999000
    @staticmethod
    def _split_title(title,player_name=None,pattern=None):
        s=str(title or '').strip()
        s=re.sub(r'\s*-\s*酷狗音乐\s*$','',s)
        parts=[x.strip() for x in s.split(' - ') if x.strip()]
        if len(parts)>=2:
            return parts[-1], ' - '.join(parts[:-1])
        return (parts[0], '') if parts else (None,None)
class FakeMedia:
    def __init__(self):
        self._track_key='oldremix|artist'
        self._uia_duration_ms=142310
        self._state={}
        self._kugou_host_v2_cache={'class':'kugou_ui','title':'草东没有派对 - 但 - 酷狗音乐'}
        self._kugou_host_v2_cache_mono=time.monotonic()*1000.0
    def _kugou_poll_uia_progress_v2(self,*a,**kw): return {'ok':1}
class FakeControl:
    def __init__(self):
        self.player_combo=FakeCombo()
        self.players={'酷狗音乐':{'pattern':None}}
        self.media_sync=FakeMedia()
        self._loaded_song='少女A (one day After Another Remix)'
        self._loaded_artist='椎名もた'
        self._h21_kugou_host_switch=None
        self.promoted=[]; self.probes=[]
    @staticmethod
    def _same_track(a,b,c,d):
        return clean(a)==clean(c) and (not clean(b) or not clean(d) or clean(b)==clean(d))
    def _detected_player_track(self): return ('但','草东没有派对')
    def _promote_kugou_background_identity_hint(self,song,artist='',source='',evidence_mono_ms=None):
        self.promoted.append((song,artist,source)); return True
    def _queue_track_probe(self,player,urgent=False): self.probes.append((player,urgent))

ns={
    'ControlPanel':FakeControl,'MediaSessionSync':FakeMedia,'LyricFetcher':FakeFetcher,
    'DEFAULT_PLAYERS':{'酷狗音乐':{'pattern':None}},'_clean_name':clean,
    'threading':threading,'time':time,'write_error_log':write_error_log,
    'H20_KUGOU_DURATION_HINT_TTL_SEC':8.0,
    '_LIMBUS_H20_KUGOU_DURATION_HINTS':{},
    '_LIMBUS_H20_KUGOU_DURATION_LOCK':threading.Lock(),
}
exec(compile(block,str(MAIN),'exec'),ns,ns)

# Host-V2 progress must cache duration under the host title too, even while internal track_key
# still belongs to the previous song during the identity handoff.
m=FakeMedia(); m._kugou_poll_uia_progress_v2()
assert clean('但') in ns['_LIMBUS_H20_KUGOU_DURATION_HINTS'], ns['_LIMBUS_H20_KUGOU_DURATION_HINTS']
assert ns['_LIMBUS_H20_KUGOU_DURATION_HINTS'][clean('但')][0]==142310

# H14's named duration worker should briefly wait for the already-running Host-V2 evidence
# instead of immediately falling into the slow legacy/MSAA scan.
ns['_LIMBUS_H20_KUGOU_DURATION_HINTS'].clear(); FakeFetcher.old_calls=0
def publish():
    time.sleep(0.08)
    with ns['_LIMBUS_H20_KUGOU_DURATION_LOCK']:
        ns['_LIMBUS_H20_KUGOU_DURATION_HINTS'][clean('Test Song')]=(123000,time.monotonic())
t=threading.Thread(target=publish); t.start()
old_name=threading.current_thread().name
try:
    threading.current_thread().name='LimbusLyric-H14-KuGouDurationHint'
    got=FakeFetcher.get_kugou_ui_duration_hint([1],'Test Song')
finally:
    threading.current_thread().name=old_name
    t.join()
assert got==123000 and FakeFetcher.old_calls==0,(got,FakeFetcher.old_calls)

# A just-selected Host-V2 new title vetoes a conflicting stale GSMTC title-change event.
p=FakeControl()
out=p._detected_player_track()
assert out==('但','草东没有派对') and p._h21_kugou_host_switch
ret=p._promote_kugou_background_identity_hint(
    '少女A (one day After Another Remix)','椎名もた',source='kugou-gsmtc-title-change',evidence_mono_ms=time.monotonic()*1000.0)
assert ret is False and not p.promoted and p.probes, (ret,p.promoted,p.probes)
assert any(x[0]=='H21酷狗陈旧GSMTC身份否决' for x in logs)
# Matching GSMTC enrichment is not vetoed.
ret=p._promote_kugou_background_identity_hint('但','草东没有派对',source='kugou-gsmtc-title-change')
assert ret is True and p.promoted[-1][0]=='但'

print('PASS: H21 KuGou identity / Host-V2 duration / cover UI replay')

# Execute the H14 budget block separately and prove that a late legacy UI timeout remains a
# drop without independent evidence, but is rescued when fresh Host-V2 and returned KRC
# durations agree. This preserves H14's old safety invariant while closing the H20 timing gap.
ownership='# Progressive keep-fast is valid only if the fast stage actually became the'
assert ownership in src
h14block=src[src.index(h14):src.index(ownership)]
class Engine:
    last_error=''; _cancel_local=threading.local(); _provider_meta_local=threading.local()
    @classmethod
    def _set_cancel_check(cls,fn=None): cls._cancel_local.fn=fn if callable(fn) else None
    @classmethod
    def _set_provider_meta(cls,**meta): cls._provider_meta_local.value=dict(meta)
    @classmethod
    def last_provider_meta(cls): return dict(getattr(cls._provider_meta_local,'value',{}) or {})
class Fetcher:
    @staticmethod
    def get_kugou_ui_duration_hint(pids,song_name,max_nodes=640):
        time.sleep(0.08); return 142310

def old_search(song_name,artist='',source='网易云',trans_only=False,provider_track_id=None,provider_duration_ms=0,prefer_precise=True):
    Fetcher.get_kugou_ui_duration_hint([1],song_name)
    return '[00:00.00]<0,1>krc',142000
Engine.search=staticmethod(old_search)
recent={'on':False}
def recent_hint(song): return 142310 if recent['on'] else 0
ns2={
    'threading':threading,'time':time,'LyricSearchEngine':Engine,'LyricFetcher':Fetcher,
    'write_error_log':write_error_log,'_h21_recent_kugou_duration_hint':recent_hint,
    'H21_KUGOU_DURATION_MATCH_MIN_MS':1200,'H21_KUGOU_DURATION_MATCH_RATIO':0.012,
}
exec(compile(h14block,str(MAIN),'exec'),ns2,ns2)
ns2['H14_AUTO_KUGOU_UI_HINT_BUDGET_SEC']=0.03
old_name=threading.current_thread().name
try:
    threading.current_thread().name='LimbusLyric-AutoLyrics-g21'
    recent['on']=False
    lyric,dur=Engine.search('但',source='酷狗',prefer_precise=True)
    assert lyric is None and dur==0, (lyric,dur)
    recent['on']=True
    lyric,dur=Engine.search('但',source='酷狗',prefer_precise=True)
    assert lyric and dur==142000,(lyric,dur)
    assert Engine.last_provider_meta().get('h21_host_v2_duration_rescue') is True,Engine.last_provider_meta()
finally:
    threading.current_thread().name=old_name
print('PASS: H21 late Host-V2/KRC version-evidence rescue replay')
