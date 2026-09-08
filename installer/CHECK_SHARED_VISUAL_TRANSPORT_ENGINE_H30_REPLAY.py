from pathlib import Path
import ast, sys

if len(sys.argv)!=2: raise SystemExit(2)
p=Path(sys.argv[1]); s=p.read_text(encoding='utf-8')
need=[
 'SHARED VISUAL TRANSPORT ENGINE CROSS-WIN H30',
 'H30共享视觉Transport等待','H30共享视觉Transport已锁定',
 "MediaSessionSync._h25_poll_netease_safe_visual_clock = _h30_netease_visual_clock",
 "MediaSessionSync._kugou_poll_visual_rail_anchor = _h30_kugou_visual_anchor",
 "LyricFetcher.get_player_pids = staticmethod(_h30_fetch_player_pids)",
 "PlayerUiPositionReader._process_pids = staticmethod(_h30_reader_process_pids)",
 "AsyncPlayerUiPositionReader._process_pids = _h30_async_process_pids",
 "_limbus_bounded_player_liveness_probe = _h30_bounded_player_liveness_probe",
 "_limbus_visual_engine='shared-cross-windows'",
]
for t in need:
    if t not in s: raise AssertionError('missing '+t)
p30=s.index('# H30 shared visual transport engine'); pmain=s.index('if __name__ == "__main__":')
assert p30<pmain
h30=s[p30:pmain]
# One visual core is invoked by both wrappers. OS/build branches stay in acquisition/adapters.
assert h30.count("_h30_shared_visual_sample(sync,'netease'")==1
assert h30.count("_h30_shared_visual_sample(sync,'kugou'")==1
shared=h30[h30.index('def _h30_shared_visual_sample'):h30.index('def _h30_netease_visual_clock')]
assert 'win10' not in shared.lower() and 'win11' not in shared.lower()
# CloudMusic PID closures must not shell out or enumerate all system processes.
for a,b in [
 ('def _h30_cloudmusic_pids','def _h30_fetch_player_pids'),
 ('def _h30_fetch_player_pids','LyricFetcher.get_player_pids ='),
 ('def _h30_reader_process_pids','PlayerUiPositionReader._process_pids ='),
 ('def _h30_async_process_pids','AsyncPlayerUiPositionReader._process_pids ='),
]:
    frag=h30[h30.index(a):h30.index(b,h30.index(a))+len(b)]
    assert 'tasklist' not in frag.lower() and 'EnumProcesses' not in frag and 'subprocess.' not in frag
assert 'EnumWindows' in h30 and 'GetExitCodeProcess' in h30
live=h30[h30.index('def _h30_bounded_player_liveness_probe'):h30.index('_limbus_bounded_player_liveness_probe = _h30_bounded_player_liveness_probe')]
assert '_limbus_liveness_tasklist_probe(' not in live and 'subprocess.' not in live and '_LIMBUS_H30_LIVENESS_PRE(sync,stem)' in live and "return None,'h30-cloudmusic-unknown-no-tasklist'" in live

# Load pure shared helpers from the real source.
tree=ast.parse(s); funcs={n.name:n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)}
def load(name,env):
    n=funcs[name]; m=ast.Module(body=[n],type_ignores=[]); ast.fix_missing_locations(m)
    ns=dict(env); exec(compile(m,str(p),'exec'),ns,ns); return ns[name]
motion=load('_h30_motion_candidates',{})
proof=load('_h30_proof_step',{
 'H30_VISUAL_PROOF_TTL_MS':60000.0,'H30_VISUAL_MIN_HITS':3,'H30_VISUAL_MIN_SPAN_MS':700.0
})

def frame(boundary, noise=None):
    w,h=1000,130; d=bytearray([28,28,28,255]*(w*h))
    # static distractor
    for yy in range(24,28):
        for x in range(70,930):
            i=(yy*w+x)*4; d[i:i+4]=bytes((190,190,190,255))
    # true rail
    for yy in range(84,88):
        for x in range(100,901):
            c=(220,70,70) if x<=boundary else (85,85,85)
            i=(yy*w+x)*4; d[i:i+4]=bytes((c[2],c[1],c[0],255))
    if noise is not None:
        for yy in range(42,50):
            for x in range(noise,noise+10):
                i=(yy*w+x)*4; d[i:i+4]=bytes((240,120,30,255))
    return {'x':0,'y':500,'w':w,'h':h,'data':bytes(d)}

# Same detector sees the same physical edge independent of provider/Windows wrapper.
a=frame(200,40); b=frame(204,80)
mc=motion(a,b)
assert mc and any(abs(x['y']-86)<=5 and abs(x['x']-202)<=10 for x in mc), mc[:5]
assert motion(b,b)==[]

# Sparse VM frames stay on one proof identity instead of requiring consecutive refreshes.
# Geometry is intentionally the same object for NetEase and KuGou wrappers.
rows=None; ok=False
samples=[(0.0,10000.0),(11200.0,21500.0),(22400.0,33200.0)]
for now,pos in samples:
    ob={'position':pos,'x0':100.0,'x1':900.0,'y':586.0,'score':100.0}
    rows,ok=proof(rows,ob,now,230000.0,False)
assert ok and rows['hits']>=3 and rows['span']>=22000
# Static/near-zero progress cannot self-certify a clock.
r=None; ok=False
for now,pos in [(0.0,10000.0),(10000.0,10020.0),(20000.0,10035.0)]:
    r,ok=proof(r,{'position':pos,'x0':100.0,'x1':900.0,'y':586.0,'score':1.0},now,230000.0,False)
assert not ok
# A real seek gets a short two-sample proof instead of inheriting the old extrapolated lease.
r=None; ok=False
for now,pos in [(30000.0,90000.0),(30600.0,91000.0)]:
    r,ok=proof(r,{'position':pos,'x0':100.0,'x1':900.0,'y':586.0,'score':1.0},now,230000.0,True)
assert ok

print('SHARED VISUAL TRANSPORT ENGINE H30 REPLAY: PASS')
print(' - NetEase and KuGou visual clocks invoke one cross-Windows temporal rail state machine')
print(' - sparse VM frames retain proof identity across long gaps; static pixels cannot self-certify')
print(' - seek proof invalidates stale extrapolation and reacquires with physical evidence')
print(' - CloudMusic PID consumers use one HWND/PID witness with no tasklist/EnumProcesses side door')
print(' - platform-specific UIA/GSMTC/native paths remain auxiliary; visual evidence semantics are shared')
