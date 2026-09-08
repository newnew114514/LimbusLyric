from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_QQ_HANDOFF_PHASE_REPLAY.py <main.py>')
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
    raise AssertionError(f'missing const {name}')

class FakeTime:
    def __init__(self): self.mono=500000.0
    def monotonic(self): return self.mono/1000.0
    def step(self,ms): self.mono+=ms
T=FakeTime(); logs=[]
def write_error_log(label,*a,detail=None,**k): logs.append((label,detail))

ns={'time':T,'write_error_log':write_error_log,
    'QQ_DIRECT_GSMTC_RAIL_HANDOFF_SUPPRESS_MS':const('QQ_DIRECT_GSMTC_RAIL_HANDOFF_SUPPRESS_MS'),
    'QQ_DIRECT_GSMTC_RAIL_HANDOFF_CONFLICT_MIN_DELTA_MS':const('QQ_DIRECT_GSMTC_RAIL_HANDOFF_CONFLICT_MIN_DELTA_MS'),
    'QQ_DIRECT_GSMTC_SEEK_REANCHOR_MIN_DELTA_MS':const('QQ_DIRECT_GSMTC_SEEK_REANCHOR_MIN_DELTA_MS'),
    'QQ_DIRECT_GSMTC_SEEK_AUTHORITY_MS':const('QQ_DIRECT_GSMTC_SEEK_AUTHORITY_MS')}
methods=['_qq_apply_direct_gsmtc_seek_authority','_qq_direct_gsmtc_veto_allowed_after_rail','_qq_seed_phase_calibration_after_initial_lock','_qq_direct_public_clock_override']
body='\n\n'.join(textwrap.indent(method_source('MediaSessionSync',m),'    ') for m in methods)
exec('class H:\n'+body,ns); H=ns['H']

def make():
    h=H();
    h._qq_last_rail_commit_mono=0.0; h._qq_last_rail_commit_target=None
    h._qq_gesture_press_mono=0.0; h._qq_gesture_release_mono=0.0
    h._qq_gsmtc_identity_seek_confirmed_mono=0.0
    h._qq_gsmtc_identity_seek_confirmed_start_mono=0.0
    h._qq_gsmtc_identity_seek_confirmed_position_ms=None
    h._qq_direct_rail_handoff_diag_mono=0.0
    h._qq_direct_gsmtc_authority_until_mono=0.0
    h._uia_position_ms=86420.0; h._uia_anchor_mono=T.mono; h._uia_status='playing'
    h._uia_observed_ms=86420.0; h._uia_last_seen_mono=T.mono
    h._qq_seek_pending=None; h._playing_seek_pending=None; h._paused_seek_pending=None
    h._uia_pending_far=None; h._qq_unarmed_far_pending=None; h._qq_gesture_recent_until_mono=0.0
    h._qq_gesture_expected_ms=None; h._qq_gesture_expected_id=0; h._qq_mouse_is_down=False
    h._qq_seek_last_commit_mono=0.0; h._qq_seek_last_commit_target=None
    h._qq_direct_gsmtc_authority_position_ms=None
    h._qq_reset_clock_authority=lambda preserve_phase_baseline=True: None
    h._qq_gsmtc_identity_guard_active=True
    h._uia_has_lock=False; h._uia_duration_ms=221000
    h._qq_auto_anchor_pending=None
    h._qq_clock_good_streak=0; h._qq_clock_last_good_ms=None; h._qq_clock_last_good_mono=None; h._qq_clock_last_good_key=''; h._qq_clock_trusted=False
    h._qq_phase_edge_last_bucket_ms=None; h._qq_phase_edge_last_mono=None; h._qq_phase_edge_last_key=''
    return h

# A. Sandbox log: UIA rail commit 86.420s arrives while GSMTC is still old ~128.6s.
# The old direct witness must not veto/override the fresh validated rail commit.
h=make(); h._qq_gesture_press_mono=T.mono-700; h._qq_gesture_release_mono=T.mono-300
h._qq_last_rail_commit_mono=T.mono-100; h._qq_last_rail_commit_target=86420.0
h._qq_gsmtc_identity_seek_confirmed_mono=T.mono-5000  # belongs to old timeline
h._qq_direct_gsmtc_authority_until_mono=T.mono+1500
assert not h._qq_direct_gsmtc_veto_allowed_after_rail(128601,T.mono)
pos,src=h._qq_direct_public_clock_override(86420,'qq-time-pair-validated',128601,True,{'source':'qq-time-pair-validated'})
assert pos==86420 and src=='qq-time-pair-validated',(pos,src)
# Even a late async veto result produced from the pre-commit guard snapshot must not flash back.
pos,src=h._qq_direct_public_clock_override(None,'qq-gsmtc-veto-uia-position',128601,True,{'source':'qq-gsmtc-veto-uia-position'})
assert pos is None and src=='qq-gsmtc-veto-uia-position',(pos,src)

# B. Regression from the latest Sandbox log: an older seek may finish its two-sample
# confirmation *after* a newer gesture. Confirmation time alone must not make it belong to
# the newer gesture. The jump started before the new gesture, so both veto bypass and direct
# re-anchor must stay suppressed over the fresh 143.420s rail/UIA commit.
h._qq_last_rail_commit_target=143420.0
h._uia_position_ms=143420.0; h._uia_anchor_mono=T.mono
h._qq_gesture_press_mono=T.mono-500; h._qq_gesture_release_mono=T.mono-250
h._qq_gsmtc_identity_seek_confirmed_mono=T.mono-50
h._qq_gsmtc_identity_seek_confirmed_start_mono=T.mono-900
h._qq_gsmtc_identity_seek_confirmed_position_ms=78804.0
assert not h._qq_direct_gsmtc_veto_allowed_after_rail(78804,T.mono)
assert not h._qq_apply_direct_gsmtc_seek_authority(78804,'playing')
assert h._uia_position_ms==143420.0

# C. If the raw discontinuity itself starts after this gesture, it is fresh independent
# evidence and regains authority immediately.
h._uia_position_ms=86420.0; h._uia_anchor_mono=T.mono
h._qq_last_rail_commit_target=86420.0
h._qq_gsmtc_identity_seek_confirmed_mono=T.mono-50
h._qq_gsmtc_identity_seek_confirmed_start_mono=T.mono-300
h._qq_gsmtc_identity_seek_confirmed_position_ms=145328.0
assert h._qq_direct_gsmtc_veto_allowed_after_rail(145328,T.mono)
assert h._qq_apply_direct_gsmtc_seek_authority(145328,'playing')
assert h._uia_position_ms==145328.0

# D. Grace is short; a persistently contradictory GSMTC is allowed back after timeout.
h._qq_gsmtc_identity_seek_confirmed_mono=0.0; h._qq_gsmtc_identity_seek_confirmed_start_mono=0.0
T.step(const('QQ_DIRECT_GSMTC_RAIL_HANDOFF_SUPPRESS_MS')+50)
assert h._qq_direct_gsmtc_veto_allowed_after_rail(128601,T.mono)

# E. Host initial-lock path: the exact-duration advancing proof has already done the hard work.
# It may seed calibration trust, but must not add any fixed time offset or formal seek authority.
h=make(); h._uia_has_lock=True
h._qq_auto_anchor_pending={'advancing_proof':True,'samples':6,'first_mono':T.mono-1390,'first_raw':78000}
ui={'position_ms':79000,'duration_ms':221000,'confidence':168,'source':'qq-time-pair-validated','source_key':'qq-live'}
assert h._qq_seed_phase_calibration_after_initial_lock(ui,'playing',False)
assert h._qq_clock_trusted and h._qq_clock_good_streak>=3
assert h._qq_clock_last_good_ms==79420.0
assert h._qq_phase_edge_last_bucket_ms==79000.0

# F. A static/non-proven candidate cannot get the fast calibration seed.
h=make(); h._uia_has_lock=True; h._qq_auto_anchor_pending={'advancing_proof':False,'samples':8,'first_mono':T.mono-2000,'first_raw':79000}
assert not h._qq_seed_phase_calibration_after_initial_lock(ui,'playing',False)
assert not h._qq_clock_trusted

print('QQ HANDOFF + PHASE REPLAY: PASS')
print('  old pre-gesture GSMTC cannot flash back over fresh UIA rail commit: PASS')
print('  older seek confirmation cannot be mis-attributed to a newer gesture: PASS')
print('  truly post-gesture GSMTC jump still regains authority immediately: PASS')
print('  rail handoff suppression expires quickly: PASS')
print('  proven initial advancing stream seeds existing PLL trust with fixed_offset=0: PASS')
print('  static/non-proven initial stream cannot seed calibration: PASS')
