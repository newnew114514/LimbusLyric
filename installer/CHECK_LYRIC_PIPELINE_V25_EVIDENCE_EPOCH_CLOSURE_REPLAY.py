#!/usr/bin/env python3
import ast, sys, textwrap
from pathlib import Path
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V25_EVIDENCE_EPOCH_CLOSURE_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def fail(msg):
    print('LYRIC PIPELINE V25 EVIDENCE EPOCH CLOSURE REPLAY: FAIL')
    print('  -',msg); raise SystemExit(1)
def fn(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name==name:
                    return ast.get_source_segment(src,m)
    fail(f'missing {cls}.{name}')
def topfn(name):
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name:
            return n
    fail(f'missing top-level {name}')
def const(name):
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets):
            return ast.literal_eval(n.value)
    fail(f'missing const {name}')
if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')): fail('V25+ marker missing')

# Dynamic unit for the epoch quarantine helper.
node=topfn('_qq_duration_replays_prebind')
mod=ast.Module(body=[node],type_ignores=[]); ast.fix_missing_locations(mod)
ns={}; exec(compile(mod,'<v25-helper>','exec'),ns,ns)
replay=ns['_qq_duration_replays_prebind']
if not replay(271016,271000,0,'qq-time-pair-candidate'):
    fail('Sandbox old 271016ms timeline should be quarantined against prebind 271000ms UIA')
if replay(188943,271000,0,'qq-time-pair-candidate'):
    fail('new 188943ms timeline incorrectly quarantined')
if not replay(271000,271000,271016,'qq-time-pair-validated'):
    fail('unchanged post-bind UIA duration should remain in old epoch')
if replay(271016,271000,271016,'qq-track-switch-hint'):
    fail('dedicated prebind track-switch hint should remain admissible')
if not replay(188943,188000,0,'qq-time-pair-candidate'):
    fail('same-duration ambiguity should fail safe instead of hard-filtering')

# Dynamic Sandbox epoch replay: old 271s evidence survives the title/bind boundary, then
# the real 188.943s timeline appears. The resolver must wait through the old epoch and return
# the changed duration, not poison the provider search with 271.016s.
class FakeTime:
    def __init__(self): self.ms=100000.0
    def monotonic(self): return self.ms/1000.0
    def sleep(self,sec): self.ms += float(sec)*1000.0
class Reader:
    def __init__(self): self.calls=0
    def poll(self,process):
        self.calls += 1
        return {'position_ms':self.calls*100,'duration_ms':271000,'source':'qq-time-pair-candidate'}
class MS: pass
logs=[]
def write_error_log(label,*args,detail=None,**kwargs): logs.append((label,detail))
T=FakeTime(); msrc=fn('ControlPanel','_resolve_qq_auto_track_duration_after_bind')
menv={'time':T,'write_error_log':write_error_log,
      'QQ_AUTO_TRACK_DURATION_REFRESH_WAIT_MS':const('QQ_AUTO_TRACK_DURATION_REFRESH_WAIT_MS'),
      'QQ_AUTO_TRACK_DURATION_REFRESH_POLL_MS':const('QQ_AUTO_TRACK_DURATION_REFRESH_POLL_MS'),
      '_qq_duration_replays_prebind':replay}
exec('class H:\n'+textwrap.indent(msrc,'    '),menv)
h=menv['H'](); h.media_sync=MS(); h.media_sync._uia_reader=Reader()
seq=iter([271016,271016,188943])
h._qq_transport_duration_evidence=lambda *a,**k: next(seq,188943)
job={'source':'QQ音乐','song':'夜、萤火虫和你','artist':'AniFace','provider_duration_ms':0,
     'qq_prebind_duration_ms':271000,'qq_prebind_transport_duration_ms':271016,
     'qq_prebind_duration_source':'qq-time-pair-candidate'}
resolved=h._resolve_qq_auto_track_duration_after_bind(job,cancel_check=lambda:False)
if resolved != 188943: fail(f'Sandbox duration epoch replay resolved {resolved}, expected 188943')
if not any(x[0]=='QQ新曲旧GSMTC时长纪元隔离' for x in logs):
    fail('Sandbox stale GSMTC duration was not explicitly quarantined')

poll=fn('MediaSessionSync','_poll_loop')
for needle in ("proc_hint_pre in ('kgmusic', 'qqmusic')", 'next_identity != prev_identity',
               "update['media_metadata_mono'] = float(self._state.get('media_metadata_mono') or 0.0)"):
    if needle not in poll: fail(f'QQ/KuGou identity-event timestamp semantics missing: {needle}')
if "# QQ keeps the V21 sampling semantics" in poll:
    fail('old QQ poll-freshness metadata semantics still present')

req=fn('ControlPanel','_request_auto_track')
for needle in ('qq_prebind_transport_duration_ms','_qq_direct_gsmtc_state',
               "'qq_prebind_transport_duration_ms': qq_prebind_transport_duration_ms"):
    if needle not in req: fail(f'prebind QQ transport epoch snapshot missing: {needle}')

resolver=fn('ControlPanel','_resolve_qq_auto_track_duration_after_bind')
for needle in ('_qq_duration_replays_prebind','QQ新曲旧GSMTC时长纪元隔离','QQ新曲旧UIA时长纪元隔离',
               'wait-new-duration-epoch','phase=post-bind-new-epoch','prebind_gsmtc='):
    if needle not in resolver: fail(f'QQ post-bind duration quarantine missing: {needle}')
# Must not disable duration safety globally.
for needle in ('QQ自动歌词时长冲突以GSMTC为准','QQ自动切歌新曲时长证据','QQ自动切歌新曲时长等待超时'):
    if needle not in resolver: fail(f'QQ duration safety baseline lost: {needle}')

kg=fn('MediaSessionSync','_kugou_poll_uia_progress_v2')
for needle in ('host-uia-range-provisional','酷狗HostV2未定时长位置先行锚定',
               'authority=display-only | duration-authority=0 | seek=unchanged',
               'not trusted and identity_bound_to_player and known_duration <= 1000.0','not bool(getattr(self, \'_kugou_rail_master_absolute\', False))'):
    if needle not in kg: fail(f'KuGou first-attach position-only seed missing: {needle}')
# Formal Range authority and V24 stale-paused proof must remain.
for needle in ('host-uia-range-v2','酷狗宿主V2原生Range时长接管','stale_paused_motion','酷狗HostV2运动否决陈旧暂停态'):
    if needle not in kg: fail(f'KuGou formal proof baseline lost: {needle}')

print('LYRIC PIPELINE V25 EVIDENCE EPOCH CLOSURE REPLAY: PASS')
print('  QQ unchanged prebind duration cannot become new-track evidence merely because bind happened: PASS')
print('  QQ actual identity timestamp no longer refreshes on every ~200ms poll: PASS')
print('  KuGou Host-V2 may seed position-only display continuity before duration proof: PASS')
print('  formal duration/absolute/Seek authority remains behind existing proof: PASS')
