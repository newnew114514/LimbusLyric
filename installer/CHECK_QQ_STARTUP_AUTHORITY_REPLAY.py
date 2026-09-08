from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_QQ_STARTUP_AUTHORITY_REPLAY.py <main.py>')
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8'); tree=ast.parse(source)

def method_source(cls_name, method):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name==cls_name:
            for item in node.body:
                if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)) and item.name==method:
                    return ast.get_source_segment(source,item)
    raise AssertionError(f'missing {cls_name}.{method}')

def const(name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)

class FakeTime:
    def __init__(self): self.mono=1000000.0
    def monotonic(self): return self.mono/1000.0
    def step(self,ms): self.mono += ms
T=FakeTime(); logs=[]
def write_error_log(label,*a,detail=None,**k): logs.append((label,detail))

ns={'time':T,'write_error_log':write_error_log}
for n in [
    'QQ_STARTUP_PROVISIONAL_HANDOFF_MAX_DRIFT_MS','QQ_STARTUP_PRELOCK_RAIL_RELEASE_WINDOW_MS',
    'QQ_STARTUP_PRELOCK_RAIL_MATCH_MIN_TOL_MS','QQ_STARTUP_PRELOCK_RAIL_MATCH_RATIO',
    'QQ_STARTUP_PRELOCK_RAIL_MATCH_MAX_TOL_MS'
]: ns[n]=const(n)
body='\n\n'.join(textwrap.indent(method_source('MediaSessionSync',m),'    ') for m in [
    '_auto_local_position','_reset_auto_local_clock','_qq_try_prelock_rail_validated_anchor','_guard_auto_local_handoff'
])
exec('class H:\n'+body,ns); H=ns['H']

class Reader:
    def request_urgent_scan(self,*a): pass

def make():
    h=H(); h._process_hint='qqmusic'; h._uia_reader=Reader()
    h._auto_local_active=True; h._auto_local_position_ms=156000.0; h._auto_local_anchor_mono=T.mono
    h._auto_local_status='playing'; h._auto_local_started_mono=T.mono-27000
    h._auto_handoff_pending=None; h._qq_auto_anchor_pending=None
    h._qq_auto_local_seed_reason='manual-first-bind'; h._qq_auto_local_seed_status='paused'; h._qq_auto_local_seeded_mono=T.mono-27000
    h._qq_startup_handoff_last_diag_mono=0.; h._qq_startup_prelock_rail_last_gesture_id=0
    h._uia_has_lock=False; h._uia_duration_ms=331000; h._uia_provisional=False; h._uia_provisional_started_mono=None
    h._uia_position_ms=None; h._uia_anchor_mono=None; h._uia_observed_ms=None; h._uia_status='playing'
    h._uia_last_seen_mono=None; h._uia_last_observed_ms=None; h._uia_last_observed_source_name=''; h._uia_last_observed_source_key=''
    h._uia_locked_source_name=''; h._uia_locked_source_key=''; h._uia_initial_pending=None; h._uia_pending_far=None
    h._playing_seek_pending=None; h._paused_seek_pending=None; h._qq_seek_pending=None
    h._qq_gesture_recent_until_mono=0.; h._qq_seek_last_commit_mono=0.; h._qq_seek_last_commit_target=None
    h._qq_last_rail_commit_mono=0.; h._qq_last_rail_commit_target=None; h._qq_post_seek_hard_rephase_done_mono=0.
    h._est_position_ms=None; h._est_anchor_mono=None; h._est_status='playing'
    h._qq_gesture_release_mono=0.; h._qq_gesture_id=0; h._qq_gesture_expected_id=0; h._qq_gesture_expected_ms=None
    h._mark_seek_burst=lambda *a,**k: None; h._clear_visual_seek_override=lambda *a,**k: None
    h._process_stem=lambda x: str(x or '').lower().removesuffix('.exe')
    return h

# A. Reproduce host first-song failure: paused seed 156s, then 27s of real playback => ~183s.
h=make(); T.step(27000)
local=h._auto_local_position('playing')
assert 182900 <= local <= 183100, local
# A stale but self-coherent formal QQ stream at 157.420s must NOT replace the provisional timeline.
ui={'source':'qq-time-pair-validated','confidence':168}
accept, kept=h._guard_auto_local_handoff(157420,ui,'playing')
assert not accept and abs(kept-local) < 50
assert any(label=='QQ首曲恢复旧Text拒绝接管' for label,_ in logs)

# B. A close formal stream is allowed to take over normally.
h=make(); T.step(1200); local=h._auto_local_position('playing')
accept,_=h._guard_auto_local_handoff(local+800,ui,'playing')
assert accept

# C. Before formal lock, a real rail gesture + validated duration-matched UIA may anchor immediately.
h=make(); h._qq_auto_local_seed_reason='auto-track'; h._qq_auto_local_seed_status='playing'
h._qq_gesture_id=1; h._qq_gesture_expected_id=1; h._qq_gesture_expected_ms=119226.; h._qq_gesture_release_mono=T.mono-300
rail_ui={'source':'qq-time-pair-validated','confidence':168,'position_ms':115000,'duration_ms':331000,
         'source_key':'qq-live','_qq_mouse_down':False}
anch=h._qq_try_prelock_rail_validated_anchor(rail_ui,'playing')
assert anch==115420 and h._uia_has_lock and not h._auto_local_active
assert h._qq_seek_last_commit_target==115420.
assert any(label=='QQ首锚前Rail可信UIA直锚' and 'geometry_authority=0' in (detail or '') for label,detail in logs)

# D. Geometry alone / mismatched UIA cannot anchor: UIA actual time must be plausibly near this gesture.
h=make(); h._qq_gesture_id=2; h._qq_gesture_expected_id=2; h._qq_gesture_expected_ms=119226.; h._qq_gesture_release_mono=T.mono-200
bad=dict(rail_ui); bad['position_ms']=171000
assert h._qq_try_prelock_rail_validated_anchor(bad,'playing') is None and not h._uia_has_lock

# E. Wrong duration is rejected even when the gesture/time looks close.
h=make(); h._qq_gesture_id=3; h._qq_gesture_expected_id=3; h._qq_gesture_expected_ms=119226.; h._qq_gesture_release_mono=T.mono-200
bad=dict(rail_ui); bad['duration_ms']=211000
assert h._qq_try_prelock_rail_validated_anchor(bad,'playing') is None and not h._uia_has_lock

print('QQ STARTUP AUTHORITY REPLAY: PASS')
print('  paused 156s seed cannot be overwritten by stale 157s after 27s playback: PASS')
print('  close formal UIA handoff remains allowed: PASS')
print('  pre-lock real rail + validated UIA anchors immediately: PASS')
print('  rail geometry never supplies time / far UIA is rejected: PASS')
print('  wrong-duration pre-lock rail sample is rejected: PASS')
