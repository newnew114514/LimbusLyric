#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_LYRIC_PAYLOAD_FIREWALL_HIGH_REFRESH_H95F8_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
marker='# H95F8 lyric payload firewall + long-line containment + adaptive high-refresh'
need(marker in src,'H95F8 marker missing')
need('+ LYRIC PAYLOAD FIREWALL + LONG-LINE CONTAINMENT + ADAPTIVE HIGH-REFRESH H95F8' in src,'H95F8 build tag missing')
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for token in (
    'H95F8_PROVIDER_MAX_VISUAL_UNITS = 360',
    "return (None, tlyric, duration)",
    'cache=deny | fallback=continue',
    "ControlPanel._load_auto_lyric_cache_from_disk = _h95f8_cache_load",
    "ControlPanel._on_auto_lyric_result = _h95f8_on_auto_lyric_result",
    'H95F8_HIGH_REFRESH_120FPS_MS = 8',
    "for name in ('line_timer', 'shake_timer')",
): need(token in block,'H95F8 integration missing: '+token)
for bad in ('MediaSessionSync.position','MediaSessionSync.seek','LyricWindow._playback_position =','parse_lrc ='):
    need(bad not in block,'H95F8 crossed clock/parser authority: '+bad)
funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
def fn(name): need(name in funcs,'function missing: '+name); return funcs[name]
def run(names,ns):
    mod=ast.Module(body=[fn(x) for x in names],type_ignores=[])
    exec(compile(mod,'<h95f8>','exec'),ns)

# Pure payload assessor: the historical incident (non-empty provider text but rows=0) must be denied.
import re, unicodedata
ns={'re':re,'_h95f8_unicodedata':unicodedata,
    'H95F8_PROVIDER_MAX_VISUAL_UNITS':360,'H95F8_PROVIDER_SUSPICIOUS_VISUAL_UNITS':180,
    'H95F8_PROVIDER_SPARSE_RAW_CHARS':900,'H95F8_PROVIDER_SPARSE_EVENT_MAX':2}
run(['_h95f8_visual_units','_h95f8_line_looks_machine_generated','_h95f8_assess_parsed_payload'],ns)
assess=ns['_h95f8_assess_parsed_payload']
incident_seed='[00:00.00]'+('music.126.net/Msong_url?id=1165736&source=netease ' * 12)
incident=(incident_seed + ('?' * 541))[:541]
need(len(incident)==541,'historical 541-char incident fixture length drifted')
ok,reason,events,maxu=assess(incident,[],False)
need(not ok and reason=='no-parseable-events' and events==0,'541-char rows=0 provider incident was admitted')
valid=[(1000,'正常歌词',None),(3000,'another lyric line',None)]
need(assess('[00:01.00]正常歌词\n[00:03.00]another lyric line',valid,False)[0],'normal timed payload rejected')
machine='https://music.126.net/api/song?id=1&source=netease&artist=x&album=y ' * 6
ok,reason,_,_=assess('x',[(1000,machine,None)],False)
need(not ok and reason in ('giant-visible-line','machine-shaped-long-line'),'machine-shaped long row escaped containment')
need(assess('instrumental boilerplate',[],True)[0],'instrumental payload lost exemption')

# Provider result guard: deny LRC while retaining translation candidate so caller can continue fallback.
class E:
    last_error=''
    meta={}
    @staticmethod
    def last_provider_meta(): return dict(E.meta)
    @staticmethod
    def _set_provider_meta(**kw): E.meta=dict(kw)
logs=[]
ns2={'LyricSearchEngine':E,'_h95f8_payload_health':lambda t,m:(False,'no-parseable-events',0,0),'write_error_log':lambda *a,**k: logs.append((a,k))}
run(['_h95f8_filter_provider_result'],ns2)
out=ns2['_h95f8_filter_provider_result']('网易云',('bad payload','[00:01.00]翻译',121500))
need(out[0] is None and out[1]=='[00:01.00]翻译' and out[2]==121500,'provider firewall did not preserve fallback channel')
need(E.meta.get('h95f8_payload_rejected')=='no-parseable-events','provider rejection evidence missing')

# Auto-cache startup pruning: malformed provider payload must not survive cache admission across restart.
import threading
class P:
    def __init__(self):
        self._auto_lyric_cache_lock=threading.Lock(); self._auto_lyric_cache={('bad',):{'lyric':'bad','provider_meta':{}},('ok',):{'lyric':'ok','provider_meta':{}}}; self.persisted=0
    def _persist_auto_lyric_cache(self): self.persisted+=1
pnl=P(); ns3={'_H95F8_CACHE_LOAD_PRE':lambda p:None,'_h95f8_payload_health':lambda t,m: ((False,'no-parseable-events',0,0) if t=='bad' else (True,'ok',2,8)),'write_error_log':lambda *a,**k:None}
run(['_h95f8_cache_load'],ns3); ns3['_h95f8_cache_load'](pnl)
need(('bad',) not in pnl._auto_lyric_cache and ('ok',) in pnl._auto_lyric_cache,'bad auto-cache row survived H95F8 load')
need(pnl.persisted==1,'pruned auto-cache was not persisted')

# Display admission guard: even a stray result that bypasses search/cache arrives with lyric=None.
seen={}
ns4={'_H95F8_AUTO_RESULT_PRE':lambda p,r: seen.setdefault('result',dict(r)),'_h95f8_payload_health':lambda t,m:(False,'giant-visible-line',1,500),'write_error_log':lambda *a,**k:None}
run(['_h95f8_on_auto_lyric_result'],ns4); ns4['_h95f8_on_auto_lyric_result'](object(),{'lyric':'bad','song':'战斗基','source':'网易云','provider_meta':{}})
need(seen['result']['lyric'] is None and 'giant-visible-line' in seen['result']['error'],'display admission guard failed')

# High-refresh policy: 240/120 Hz gets ~120fps only at low pressure; pressure falls back progressively.
class W:
    def __init__(self,hz,p): self._display_refresh_hz=hz; self.p=p
    def _render_pressure_level(self): return self.p
ns5={'_H95F8_ANIMATION_INTERVAL_PRE':lambda w:15,'H95F8_HIGH_REFRESH_THRESHOLD_HZ':100.0,'H95F8_HIGH_REFRESH_120FPS_MS':8,'H95F8_HIGH_REFRESH_100FPS_MS':10,'H95F8_HIGH_REFRESH_SOFT_MS':10,'H95F8_HIGH_REFRESH_HIGH_MS':12,'H95F8_HIGH_REFRESH_SEVERE_MS':16}
run(['_h95f8_animation_frame_interval'],ns5); cadence=ns5['_h95f8_animation_frame_interval']
need(cadence(W(60,0))==15,'60Hz legacy cadence changed')
need(cadence(W(100,0))==10,'100Hz cadence wrong')
need(cadence(W(120,0))==8 and cadence(W(240,0))==8,'120/240Hz low-pressure cadence not 120fps class')
need(cadence(W(240,1))==10 and cadence(W(240,2))==12 and cadence(W(240,3))==16,'pressure fallback cadence wrong')

# Runtime retimer updates active Qt timers without touching inactive/manual text timers.
class T:
    def __init__(self,on=True,iv=12): self.on=on; self.iv=iv; self.sets=[]
    def isActive(self): return self.on
    def interval(self): return self.iv
    def setInterval(self,v): self.iv=int(v); self.sets.append(int(v))
class RW:
    def __init__(self): self.line_timer=T(True,12); self.shake_timer=T(True,12); self._h95f8_last_retime_mono=0
rw=RW(); ns6={'time':__import__('time'),'H95F8_RETIMER_PERIOD_MS':500.0,'_h95f8_animation_frame_interval':lambda w:8}
run(['_h95f8_retime_animation'],ns6)
need(ns6['_h95f8_retime_animation'](rw,1000)==8 and rw.line_timer.iv==8 and rw.shake_timer.iv==8,'active timers did not retime')
need(ns6['_h95f8_retime_animation'](rw,1200) is None,'retimer ignored 500ms throttle')

print('LYRIC PAYLOAD FIREWALL + HIGH REFRESH H95F8 REPLAY: PASS')
print('  malformed provider rows=0 -> cache/display deny: PASS')
print('  long machine-shaped row containment: PASS')
print('  instrumental/manual compatibility boundary: PASS')
print('  provider fallback channel preservation: PASS')
print('  adaptive 60/100/120fps cadence with pressure fallback: PASS')
