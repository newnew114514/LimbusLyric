#!/usr/bin/env python3
from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_RELEASE_REVIEW_H10F2_REPLAY.py <main.py>')
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8'); tree=ast.parse(source)

def method_source(cls_name, method):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name==cls_name:
            for item in node.body:
                if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)) and item.name==method:
                    return ast.get_source_segment(source,item)
    raise AssertionError(f'missing {cls_name}.{method}')

def function_source(name):
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return ast.get_source_segment(source,node)
    raise AssertionError(f'missing function {name}')

def const(name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f'missing const {name}')

def need(cond,msg):
    if not cond: raise AssertionError(msg)
    print('  '+msg+': PASS')

class FakeTime:
    def __init__(self): self.mono=900000.0
    def monotonic(self): return self.mono/1000.0
    def step(self,ms): self.mono += float(ms)
T=FakeTime(); logs=[]
def write_error_log(label,*a,detail=None,**k): logs.append((label,detail))

names=[
 'QQ_HOVER_SAFE_CLOCK_MAX_GAP_MS','QQ_INITIAL_ANCHOR_MIN_PROGRESS_MS',
 'QQ_INITIAL_ANCHOR_MAX_PACE_ERROR_MS','QQ_INITIAL_ANCHOR_MIN_SAMPLES',
 'QQ_INITIAL_ANCHOR_MIN_SPAN_MS','QQ_INITIAL_ANCHOR_MIN_CONFIDENCE',
 'QQ_AUTO_LOCAL_FAST_SEED_MAX_AGE_MS','QQ_AUTO_LOCAL_FAST_SEED_MIN_CONFIDENCE',
 'QQ_AUTO_LOCAL_REBASE_MIN_DRIFT_MS','QQ_AUTO_LOCAL_REBASE_LOG_COOLDOWN_MS',
]
ns={'time':T,'write_error_log':write_error_log}
for n in names: ns[n]=const(n)
exec(function_source('_qq_initial_anchor_stream_step'),ns)
body=textwrap.indent(method_source('MediaSessionSync','_qq_rebase_auto_local_from_coherent_uia'),'    ')
exec('class H:\n'+body,ns); H=ns['H']

def make(reason):
    h=H(); h._auto_local_active=True; h._uia_has_lock=False
    h._auto_local_position_ms=0.0; h._auto_local_anchor_mono=T.mono; h._auto_local_status='playing'
    h._auto_local_started_mono=T.mono-100; h._auto_handoff_pending=None
    h._qq_auto_display_pending=None; h._qq_auto_display_last_rebase_mono=0.0
    h._qq_auto_local_wait_seed=True; h._qq_auto_local_seed_reason=reason
    h._qq_auto_local_seeded_mono=0.0; h._qq_auto_local_seed_status='unknown'; h._uia_duration_ms=125000
    return h

def ui(pos):
    return {'position_ms':pos,'duration_ms':125000,'confidence':168,'source':'qq-time-pair-validated',
            'source_key':'qq-live','_qq_mouse_down':False,'_qq_cursor_progress':False}

# Real-world replay from 2026-08-20: QQ startup UI text briefly went 26s -> 21s -> 9s -> 1s.
# A startup attach must not let the first stale validated sample move the display lane.
h=make('startup-attach')
need(not h._qq_rebase_auto_local_from_coherent_uia(ui(26000),'playing'), 'startup attach rejects one-sample 26s display seed')
need(h._auto_local_position_ms == 0.0 and h._qq_auto_local_wait_seed, 'rejected startup sample cannot move provisional display')
T.step(300); need(not h._qq_rebase_auto_local_from_coherent_uia(ui(21000),'playing'), 'backward 26s->21s stream cannot seed startup display')
T.step(300); need(not h._qq_rebase_auto_local_from_coherent_uia(ui(9000),'playing'), 'backward 21s->9s stream cannot seed startup display')
T.step(300); need(not h._qq_rebase_auto_local_from_coherent_uia(ui(1000),'playing'), 'startup stream reseeds at coherent low position')
T.step(300); need(not h._qq_rebase_auto_local_from_coherent_uia(ui(1300),'playing'), 'two samples remain below advancing proof threshold')
T.step(300); h._qq_rebase_auto_local_from_coherent_uia(ui(1600),'playing')
need(not h._qq_auto_local_wait_seed, 'three-sample advancing startup stream retires seed wait')
need(h._auto_local_position_ms < 5000.0, 'startup display never adopts stale 26s sample')
need(not h._uia_has_lock, 'startup proof remains display-only without formal clock authority')

# H9/fast-track behavior remains intact: an actual different-song auto-track event may still
# use the first duration-matched validated sample for display-only bootstrap.
T.step(1000); h2=make('auto-track')
need(h2._qq_rebase_auto_local_from_coherent_uia(ui(26000),'playing'), 'auto-track still permits fast one-sample display seed')
need(h2._auto_local_position_ms == 26420.0 and not h2._uia_has_lock, 'auto-track fast seed does not gain formal clock authority')

# KuGou hook review: keep the reliable WH_MOUSE_LL hook installed, but do not enqueue global
# mouse edges when KuGou is inactive/dead, and do not swap queues on every non-KuGou snapshot.
init=method_source('MediaSessionSync','__init__')
hook=method_source('MediaSessionSync','_ensure_kugou_mouse_hook')
start=method_source('MediaSessionSync','start')
worker=method_source('MediaSessionSync','_player_liveness_worker')
retire=method_source('MediaSessionSync','_retire_confirmed_dead_player')
snap=method_source('MediaSessionSync','snapshot')
need('_kugou_mouse_hook_capture_enabled = False' in init, 'KuGou hook capture starts disabled')
need("not bool(getattr(self, '_kugou_mouse_hook_capture_enabled', False))" in hook and 'hook_down[0] = False' in hook,
     'inactive KuGou hook callback bypasses event enqueue')
need("if new_stem == 'kgmusic':" in start and '_player_liveness_snapshot(new_stem)' in start,
     'KuGou selection enables capture without overriding confirmed-dead state')
need("if stem == 'kgmusic' and confirmed is not None" in worker and '_kugou_mouse_hook_capture_enabled = bool(confirmed)' in worker,
     'KuGou reopen/death liveness toggles hook capture')
need("if stem == 'kgmusic':" in retire and '_kugou_mouse_hook_capture_enabled = False' in retire,
     'confirmed KuGou death disables hook capture before queue retirement')
need("!= 'kgmusic' and bool(getattr(self, '_kugou_mouse_hook_capture_enabled', False))" in snap,
     'non-KuGou snapshot uses one-shot fallback instead of per-frame queue replacement')

need('RELEASE-REVIEW CLOSURE H10F2' in source, 'H10F2 build tag present')
print('RELEASE REVIEW H10F2 REPLAY: PASS')
