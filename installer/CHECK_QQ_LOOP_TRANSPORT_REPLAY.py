from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_QQ_LOOP_TRANSPORT_REPLAY.py <main.py>')
path = Path(sys.argv[1]); source = path.read_text(encoding='utf-8')
tree = ast.parse(source)

def method_source(cls_name, method):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method:
                    return ast.get_source_segment(source, item)
    raise AssertionError(f'missing {cls_name}.{method}')

def const(name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f'missing const {name}')

class FakeTime:
    def __init__(self): self.ms = 100000.0
    def monotonic(self): return self.ms / 1000.0
    def step(self, ms): self.ms += ms
T = FakeTime(); logs=[]
def write_error_log(label, *args, detail=None, **kwargs): logs.append((label, detail))

names = [
    'QQ_LOOP_TRANSPORT_ENABLED','QQ_LOOP_TRANSPORT_END_GRACE_MS',
    'QQ_LOOP_TRANSPORT_EVIDENCE_TTL_MS','QQ_LOOP_TRANSPORT_STATUS_GRACE_MS',
    'QQ_LOOP_TRANSPORT_REAL_START_MAX_MS','QQ_LOOP_TRANSPORT_STALE_END_WINDOW_MS'
]
ns={'time':T,'write_error_log':write_error_log}
for name in names: ns[name]=const(name)
methods=['_qq_reset_loop_transport','_qq_begin_loop_transport','_qq_loop_transport_local_position','_qq_loop_transport_public_override']
body='\n\n'.join(textwrap.indent(method_source('MediaSessionSync',m),'    ') for m in methods)
exec('class SyncHarness:\n'+body, ns)
Sync=ns['SyncHarness']

def make_sync():
    s=Sync(); s._process_hint='qqmusic.exe'; s._track_key='miku|artist'; s._uia_duration_ms=220000
    s._state={'duration_ms':220000,'position_ms':0,'position_source':'','status':'playing','seek_serial':0,'qq_transport_generation':0}
    s._seek_serial=0; s._qq_loop_transport_generation=0; s._qq_loop_last_restart_mono=0.0
    s._qq_loop_end_evidence_mono=0.0; s._qq_loop_end_duration_ms=0; s._qq_loop_end_track_key=''
    s._qq_loop_local_active=False; s._qq_loop_local_position_ms=0.0; s._qq_loop_local_anchor_mono=None
    s._qq_loop_local_started_mono=0.0; s._qq_loop_local_status='unknown'; s._qq_loop_local_duration_ms=0; s._qq_loop_local_track_key=''
    s._qq_seek_last_commit_mono=0.0; s._qq_last_rail_commit_mono=0.0; s._seek_burst_until_mono=0.0
    s._process_stem=lambda v: str(v or '').lower().replace('.exe','')
    def set_state(**kw): s._state.update(kw)
    s._set_state=set_state
    return s

# A. End clamp becomes one centralized repeat instance and compensates proof delay.
s=make_sync()
p,src,st=s._qq_loop_transport_public_override(220000,'uia', 'playing','playing',220000,{'source':'qq-time-pair-validated','confidence':168})
assert not s._qq_loop_local_active and s._qq_loop_end_evidence_mono>0
T.step(950)
p,src,st=s._qq_loop_transport_public_override(220000,'uia', 'playing','playing',220000,{'source':'qq-time-pair-validated','confidence':168})
assert s._qq_loop_local_active and src=='qq-loop-local-transport' and st=='playing',(p,src,st)
assert 850 <= p <= 1100,p
assert s._seek_serial==1 and s._qq_loop_transport_generation==1
assert s._state.get('position_source')=='qq-loop-local-transport' and s._state.get('qq_transport_generation')==1

# B. Boundary stopped/unknown bounce cannot create a second generation and public clock keeps moving.
T.step(120)
p1,src1,st1=s._qq_loop_transport_public_override(p,src,'stopped','playing',None,{})
T.step(180)
p2,src2,st2=s._qq_loop_transport_public_override(p1,src1,'playing','stopped',None,{})
assert s._qq_loop_transport_generation==1 and s._seek_serial==1
assert st1=='playing' and st2=='playing' and p2>p1,(p1,p2,st1,st2)

# C. Old validated end Text is quarantined; a genuine early validated clock retires local transport.
T.step(200)
p3,src3,st3=s._qq_loop_transport_public_override(220000,'qq-time-pair-validated','playing','playing',220000,{'source':'qq-time-pair-validated','confidence':168})
assert src3=='qq-loop-local-transport' and s._qq_loop_local_active
T.step(200)
p4,src4,st4=s._qq_loop_transport_public_override(1800,'qq-time-pair-validated','playing','playing',1800,{'source':'qq-time-pair-validated','confidence':168})
assert not s._qq_loop_local_active and p4==1800 and src4=='qq-time-pair-validated',(p4,src4)

# D. A recent explicit seek to the tail must not masquerade as a natural repeat dwell.
s_seek=make_sync()
s_seek._qq_seek_last_commit_mono=T.ms
p,src,st=s_seek._qq_loop_transport_public_override(220000,'uia','playing','playing',220000,{'source':'qq-time-pair-validated','confidence':168})
T.step(1100)
p,src,st=s_seek._qq_loop_transport_public_override(220000,'uia','playing','playing',220000,{'source':'qq-time-pair-validated','confidence':168})
assert not s_seek._qq_loop_local_active and s_seek._qq_loop_transport_generation==0
# The strong stopped->playing boundary still wins even while that seek guard is recent.
p,src,st=s_seek._qq_loop_transport_public_override(220000,'uia','stopped','playing',220000,{'source':'qq-time-pair-validated','confidence':168})
T.step(120)
p,src,st=s_seek._qq_loop_transport_public_override(220000,'uia','playing','stopped',None,{})
assert s_seek._qq_loop_local_active and s_seek._qq_loop_transport_generation==1 and 0 <= p <= 50

# E. A later real repeat re-arms; stopped->playing with recent end proof starts immediately from zero.
T.step(5000)
p,src,st=s._qq_loop_transport_public_override(220000,'uia','stopped','playing',220000,{'source':'qq-time-pair-validated','confidence':168})
assert not s._qq_loop_local_active and s._qq_loop_end_evidence_mono>0
T.step(180)
p,src,st=s._qq_loop_transport_public_override(220000,'uia','playing','stopped',None,{})
assert s._qq_loop_local_active and s._qq_loop_transport_generation==2 and s._seek_serial==2
assert 0 <= p <= 50,(p,src,st)

# F. A real pause freezes the centralized local transport instead of forcing playback forever.
T.step(300)
p1,_,st1=s._qq_loop_transport_public_override(p,'qq-loop-local-transport','paused','playing',None,{})
T.step(500)
p2,_,st2=s._qq_loop_transport_public_override(p1,'qq-loop-local-transport','paused','paused',None,{})
assert st1=='paused' and st2=='paused' and abs(p2-p1)<=2,(p1,p2,st1,st2)

bind = method_source('MediaSessionSync','bind_track')
poll = method_source('MediaSessionSync','_poll_loop')
for token in ("self._qq_reset_loop_transport('bind-track')", '_qq_loop_local_duration_ms = int(duration)'):
    assert token in bind, token
assert 'self._qq_loop_transport_public_override(' in poll
assert 'qq_transport_generation=int(getattr(self, \'_qq_loop_transport_generation\'' in poll

print('QQ LOOP TRANSPORT REPLAY: PASS')
print('  end clamp -> centralized display/local loop instance: PASS')
print('  stopped/unknown bounce does not double-trigger: PASS')
print('  stale old-end UIA quarantined; early real clock reentry: PASS')
print('  recent seek-to-end dwell is blocked; stopped->playing still wins: PASS')
print('  next repeat re-arms and stopped->playing starts immediately: PASS')
print('  pause freezes local repeat clock; bind reset wired: PASS')
