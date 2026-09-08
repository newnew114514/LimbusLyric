from pathlib import Path
import ast, sys

if len(sys.argv) != 2:
    raise SystemExit(2)
path=Path(sys.argv[1]); s=path.read_text(encoding='utf-8')
need=[
    'NETEASE TEMPORAL RAIL + CACHED PROCESS WITNESS H29',
    'H29网易云时序Rail等待', 'H29网易云时序Rail时钟已锁定',
    'H29网易云缓存PID存活快路', 'boundary=temporal-motion',
    'MediaSessionSync._h25_poll_netease_safe_visual_clock = _h29_netease_visual_clock',
    '_limbus_bounded_player_liveness_probe = _h29_bounded_player_liveness_probe',
    "MediaSessionSync._h25_poll_netease_safe_visual_clock._limbus_layer='H29'",
]
for token in need:
    if token not in s: raise AssertionError('missing '+token)
p29=s.index('# H29 NetEase temporal rail')
p30=s.index('# H30 shared visual transport engine', p29)
assert p29<p30
h29=s[p29:p30]
# Scope this replay to H29 itself. Later layers (for example H42) may define
# separate bounded PSAPI helpers without changing H29's CloudMusic contract.
# H29 must still never repeat H28's full-system EnumProcesses mistake.
assert 'EnumProcesses' not in h29
probe_block=h29[h29.index('def _h29_bounded_player_liveness_probe'):h29.index("_limbus_bounded_player_liveness_probe = _h29_bounded_player_liveness_probe")]
assert '_limbus_liveness_tasklist_probe(' not in probe_block
assert 'GetExitCodeProcess' in h29 and 'EnumWindows' in h29
# Safe Win10 owns H29 directly; non-safe/Win11 delegates H28 unchanged.
visual_src=h29[h29.index('def _h29_netease_visual_clock'):h29.index('MediaSessionSync._h25_poll_netease_safe_visual_clock = _h29_netease_visual_clock')]
assert "if not _h29_netease_safe(sync):\n            return _LIMBUS_H29_NCM_VISUAL_PRE(sync,status_hint)" in visual_src
assert '_LIMBUS_H29_NCM_VISUAL_PRE(sync,status_hint)' in visual_src
# Static colour split is geometry-only; temporal motion supplies the boundary.
obs_src=h29[h29.index('def _h29_motion_rail_observations'):h29.index('def _h29_proof_step')]
assert "'motion-local-geometry'" in obs_src
assert "'static-geometry-fallback'" in obs_src
assert "boundary=temporal-motion" in visual_src

# Load real pure helpers from the AST.
tree=ast.parse(s); funcs={}
for n in ast.walk(tree):
    if isinstance(n,ast.FunctionDef): funcs[n.name]=n

def load(name, env):
    n=funcs[name]; m=ast.Module(body=[n],type_ignores=[]); ast.fix_missing_locations(m)
    ns=dict(env); exec(compile(m,str(path),'exec'),ns,ns); return ns[name]

rgb=load('_kugou_visual_rgb',{})
infer=load('_kugou_visual_infer_bounds',{})
motion=load('_h29_temporal_motion_candidates',{})
proof=load('_h29_proof_step',{'H29_NETEASE_MIN_HITS':3,'H29_NETEASE_MIN_SPAN_MS':720.0})
# Real H27 static helper is retained only as fallback geometry.
rgbdist=load('_h26_rgb_distance',{})
quant=load('_h27_quant_rgb',{})
static=load('_h27_netease_static_rail_candidates',{'_h26_rgb_distance':rgbdist,'_h27_quant_rgb':quant})

class Sync:
    _kugou_visual_rgb=staticmethod(rgb)
    _kugou_visual_infer_bounds=infer
sync=Sync()

def make_frame(boundary, noise_x=None):
    w,h=1000,130
    data=bytearray([28,28,28,255]*(w*h))
    # High-contrast static distractor: must never become time authority by itself.
    for yy in range(24,28):
        for x in range(70,930):
            i=(yy*w+x)*4; data[i:i+4]=bytes((190,190,190,255))
    # True progress rail. Temporal boundary moves, x0/x1 stay fixed.
    for yy in range(84,88):
        for x in range(100,901):
            c=(220,70,70) if x<=boundary else (85,85,85)
            i=(yy*w+x)*4; data[i:i+4]=bytes((c[2],c[1],c[0],255))
    # Optional unrelated animation away from the rail.
    if noise_x is not None:
        for yy in range(45,53):
            for x in range(noise_x,noise_x+12):
                i=(yy*w+x)*4; data[i:i+4]=bytes((240,120,30,255))
    return {'x':0,'y':500,'w':w,'h':h,'data':bytes(data)}

# Bind the actual H29 observation helper against the real static detector.
observe=load('_h29_motion_rail_observations',{
    '_h29_temporal_motion_candidates':motion,
    '_h26_netease_static_rail_candidates':static,
})
prev=make_frame(200,40); rows=[]; locked=False
for idx,(b,nx) in enumerate([(202,60),(204,80),(207,100),(210,120)],1):
    cur=make_frame(b,nx)
    obs,mc,sc=observe(sync,prev,cur,221500,(0,0,1000,700))
    assert mc>=1 and obs, (idx,mc,sc)
    # Temporal-local inference must identify the true 100..900 rail rather than the broad row.
    best=next((o for o in obs if o['geometry_source']=='motion-local-geometry'),None)
    assert best is not None
    assert abs(best['x0']-100)<=4 and abs(best['x1']-900)<=4
    match=rows[0] if rows else None
    row,ok=proof(match,best,idx*420.0,221500)
    rows=[row]
    locked=locked or ok
    prev=cur
assert locked, rows
# No motion => no observations, regardless of static distractors.
cur=make_frame(210,120)
obs,mc,sc=observe(sync,cur,cur,221500,(0,0,1000,700))
assert not obs and mc==0

# 0.0 must remain a real stored position, never be replaced through truthiness.
zero={'hits':1,'first_mono':0.0,'last_mono':0.0,'first_position':0.0,'last_position':0.0,'x0':100.0,'x1':900.0,'y':585.0}
o={'position':450.0,'x0':100.0,'x1':900.0,'y':585.0,'score':1.0}
r,_=proof(zero,o,420.0,221500)
assert r['first_position']==0.0

print('NETEASE TEMPORAL RAIL + CACHED PROCESS WITNESS H29 REPLAY: PASS')
print(' - temporal pixel motion, not a static colour split, owns NetEase position')
print(' - local rail geometry around the moving boundary outranks broad static rows')
print(' - static distractors cannot acquire time authority')
print(' - cached validated CloudMusic PID replaces full-system EnumProcesses on positive liveness')
print(' - Win11/non-safe visual path delegates H28 unchanged')
