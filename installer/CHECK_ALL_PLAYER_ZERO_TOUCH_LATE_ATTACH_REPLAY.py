#!/usr/bin/env python3
import ast, re, sys, textwrap
from pathlib import Path

if len(sys.argv)!=2: raise SystemExit('usage: CHECK_ALL_PLAYER_ZERO_TOUCH_LATE_ATTACH_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)

def fail(msg):
    print('ALL PLAYER ZERO-TOUCH + LATE ATTACH REPLAY: FAIL')
    print('  -',msg); raise SystemExit(1)

def fs(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for x in n.body:
                if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name:
                    lines=src.splitlines(True); return ''.join(lines[x.lineno-1:x.end_lineno])
    fail(f'missing {cls}.{name}')

arm=fs('ControlPanel','_arm_zero_touch_selected_player')
warm=fs('ControlPanel','_warmup_selected_player')
req=fs('ControlPanel','_request_auto_track')
bind=fs('MediaSessionSync','bind_track')
poll=fs('MediaSessionSync','_poll_loop')
qqh=fs('PlayerUiPositionReader','_qq_hidden_startup_time_pair')
kgh=fs('PlayerUiPositionReader','_kugou_hidden_startup_range')
asyncset=fs('AsyncPlayerUiPositionReader','set_startup_late_attach')

for name in ('网易云音乐','QQ音乐','酷狗音乐'):
    if name not in arm: fail(f'zero-touch does not include {name}')
if 'self.media_sync.start(process_name)' not in arm or 'first_attach=' not in arm:
    fail('selected-player zero-touch does not start sync / record first attach')
if 'switched_zero_touch_player' not in warm or 'QTimer.singleShot(0, self._arm_zero_touch_selected_player)' not in warm:
    fail('switching between built-in players does not automatically re-arm zero-touch attach')
if "startup_existing=bool(startup_existing_attach)" not in req or 'initial_position_ms = 0' not in req:
    fail('first late attach is not explicitly separated from fake song-zero detection latency')
if "_qq_auto_local_seed_reason = 'startup-attach' if startup_existing else 'auto-track'" not in bind:
    fail('QQ startup-existing attach can still enter auto-track zero display lane')
if 'if not startup_existing and (KUGOU_RAIL_LOCAL_MASTER_ZERO_BOOTSTRAP or auto_provisional)' not in bind:
    fail('KuGou startup-existing attach can still seed rail master at zero')
if "reason='hidden-startup-range'" not in poll or "source') or '') == 'kugou-hidden-range-startup'" not in poll:
    fail('proven hidden KuGou range is not handed to existing rail local master')
if 'set_startup_late_attach' not in asyncset:
    fail('async UIA wrapper does not propagate startup late-attach mode')

# Hidden QQ witness must require lyric duration and causal proof before publishing position.
for needle in ('_duration_matches_expected(total)', "'qq-hidden-startup-proving'", "int(q['count']) < 3", 'span < 900.0', "'qq-time-pair-validated'"):
    if needle not in qqh: fail(f'QQ hidden startup proof missing {needle}')
if 'position_ms\': None' not in qqh:
    fail('QQ hidden startup proof publishes a position before validation')
# Hidden KuGou witness must be a native RangeValue with duration and causal proof.
for needle in ('iface_range_value', 'native_duration_ms', 'native_mismatch', '_kugou_progress_proof_step', "'kugou-hidden-range-startup'"):
    if needle not in kgh: fail(f'KuGou hidden startup proof missing {needle}')
if 'abs(nd-expected) > max(2500.0, expected*0.018)' not in kgh:
    fail('KuGou hidden Range has no strict expected-duration gate')

# Execute QQ hidden proof with a synthetic hidden Text pair. No UIA/Windows required.
class Clock:
    def __init__(self): self.t=10.0
    def monotonic(self): return self.t
clock=Clock()
class Info:
    process_id=7; control_type='Text'
class C:
    def __init__(self,text,x): self.element_info=Info(); self.text=text; self.x=x
class W:
    def __init__(self, controls): self.controls=controls
    def descendants(self,control_type=None): return self.controls
class Adapter:
    def _best_pair(self,items,wr):
        if len(items)<2:return None
        items=sorted(items,key=lambda z:z['value']); return (100,items[0],items[-1])
ns={'time':clock,'write_error_log':lambda *a,**k:None}
exec('class H:\n'+textwrap.indent(qqh,'    '),ns); H=ns['H']
h=H(); h._startup_late_attach=True; h._expected_duration_ms=255000; h._qq_hidden_probe_last_mono=0.0; h._qq_hidden_pair_pending=None
h._transport_status='playing'; h._qq_adapter=Adapter(); h._qq_attach_hidden_uia_windows=lambda p:[W([C('00:33',1),C('04:15',2)])]
h._rect_tuple=lambda o:(0,0,100,20); h._control_texts=lambda c:[c.text]
h._time_values=lambda s:[((int(s.split(':')[0])*60+int(s.split(':')[1]))*1000,s)]
h._duration_matches_expected=lambda d: abs(int(d)-255000)<=1000; h._control_key=lambda c:str(c.x)
r1=h._qq_hidden_startup_time_pair('qqmusic.exe',{7})
if not r1 or r1.get('position_ms') is not None: fail('QQ hidden proof published first sample')
clock.t+=1.30; h._qq_attach_hidden_uia_windows=lambda p:[W([C('00:34',1),C('04:15',2)])]
r2=h._qq_hidden_startup_time_pair('qqmusic.exe',{7})
if not r2 or r2.get('position_ms') is not None: fail('QQ hidden proof published second sample')
clock.t+=1.30; h._qq_attach_hidden_uia_windows=lambda p:[W([C('00:35',1),C('04:15',2)])]
r3=h._qq_hidden_startup_time_pair('qqmusic.exe',{7})
if not r3 or r3.get('position_ms')!=35000 or r3.get('source')!='qq-time-pair-validated':
    fail(f'QQ hidden 3-sample proof did not publish validated mid-song position: {r3}')
# Wrong total resets proof and never publishes.
clock.t+=1.30; h._qq_attach_hidden_uia_windows=lambda p:[W([C('00:36',1),C('03:00',2)])]
if h._qq_hidden_startup_time_pair('qqmusic.exe',{7}) is not None:
    fail('QQ hidden wrong-duration pair was accepted')

print('ALL PLAYER ZERO-TOUCH + LATE ATTACH REPLAY: PASS')
print('  selected QQ / NetEase / KuGou all enter zero-touch lifecycle and re-arm on player switch: PASS')
print('  startup-existing track never turns detection latency into song-zero clock: PASS')
print('  QQ hidden current/total requires duration match + 3 coherent samples: PASS')
print('  KuGou hidden Range requires native duration + causal proof before rail seed: PASS')
