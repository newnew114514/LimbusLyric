from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_QQ_FAST_PROVISIONAL_ANCHOR_REPLAY.py <main.py>')
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
    def __init__(self): self.mono=800000.0
    def monotonic(self): return self.mono/1000.0
    def step(self,ms): self.mono+=ms
T=FakeTime(); logs=[]
def write_error_log(label,*a,detail=None,**k): logs.append((label,detail))

def fake_stream_step(pending,*args,**kwargs):
    return pending, False

ns={
    'time':T,'write_error_log':write_error_log,
    '_qq_initial_anchor_stream_step':fake_stream_step,
    'QQ_AUTO_LOCAL_FAST_SEED_MAX_AGE_MS':const('QQ_AUTO_LOCAL_FAST_SEED_MAX_AGE_MS'),
    'QQ_AUTO_LOCAL_FAST_SEED_MIN_CONFIDENCE':const('QQ_AUTO_LOCAL_FAST_SEED_MIN_CONFIDENCE'),
    'QQ_INITIAL_ANCHOR_MIN_CONFIDENCE':const('QQ_INITIAL_ANCHOR_MIN_CONFIDENCE'),
    'QQ_AUTO_LOCAL_REBASE_MIN_DRIFT_MS':const('QQ_AUTO_LOCAL_REBASE_MIN_DRIFT_MS'),
    'QQ_AUTO_LOCAL_REBASE_LOG_COOLDOWN_MS':const('QQ_AUTO_LOCAL_REBASE_LOG_COOLDOWN_MS'),
}
methods=['_qq_rebase_auto_local_from_coherent_uia']
body='\n\n'.join(textwrap.indent(method_source('MediaSessionSync',m),'    ') for m in methods)
exec('class H:\n'+body,ns); H=ns['H']

def make(reason='auto-track', status='playing'):
    h=H()
    h._auto_local_active=True; h._uia_has_lock=False
    h._auto_local_position_ms=0.0; h._auto_local_anchor_mono=T.mono
    h._auto_local_status=status; h._auto_local_started_mono=T.mono-900
    h._auto_handoff_pending=None; h._qq_auto_anchor_pending=None
    h._qq_auto_display_pending=None; h._qq_auto_display_last_rebase_mono=0.0
    h._qq_auto_local_wait_seed=True; h._qq_auto_local_seed_reason=reason; h._qq_auto_local_seeded_mono=0.0
    h._uia_duration_ms=260000
    return h

# A. New QQ track must not visibly run a fabricated 0s clock before any trustworthy pair exists.
poll_src=method_source('MediaSessionSync','_poll_loop')
bind_src=method_source('MediaSessionSync','bind_track')
assert "position_source = 'qq-auto-track-wait-display-seed'" in poll_src
assert "self._qq_auto_local_wait_seed = True" in bind_src

# B. Host log replay: after lyric duration is known, the first validated 149s pair may seed
h=make()
# display immediately even if the cursor is still resting over QQ's rail. It is display-only.
ui={'position_ms':149000,'duration_ms':260000,'confidence':168,'source':'qq-time-pair-validated',
    'source_key':'qq-live','_qq_mouse_down':False,'_qq_cursor_progress':True}
assert h._qq_rebase_auto_local_from_coherent_uia(ui,'playing')
assert not h._qq_auto_local_wait_seed
assert h._auto_local_position_ms==149420.0
assert h._qq_auto_local_seeded_mono==T.mono
assert not h._uia_has_lock
assert any(label=='QQ首锚前快速临时时钟采样' and 'authority=display-only' in (detail or '') for label,detail in logs)
# C. Manual first bind while paused is also fast, but a paused rail-hover sample is not trusted.
h=make(reason='manual-first-bind', status='paused')
ui_hover={'position_ms':55000,'duration_ms':260000,'confidence':168,'source':'qq-time-pair-validated',
          'source_key':'qq-live','_qq_mouse_down':False,'_qq_cursor_progress':True}
assert not h._qq_rebase_auto_local_from_coherent_uia(ui_hover,'paused')
assert h._qq_auto_local_wait_seed
ui_off=dict(ui_hover); ui_off['_qq_cursor_progress']=False
assert h._qq_rebase_auto_local_from_coherent_uia(ui_off,'paused')
assert h._auto_local_position_ms==55000.0 and not h._qq_auto_local_wait_seed

# D. Wrong-track duration can never seed the provisional lane.
h=make()
ui_bad=dict(ui); ui_bad['duration_ms']=219000
assert not h._qq_rebase_auto_local_from_coherent_uia(ui_bad,'playing')
assert h._qq_auto_local_wait_seed and h._auto_local_position_ms==0.0

# E. Fast seed expires; an arbitrarily late stale sample cannot wake a forgotten provisional clock.
h=make(); T.step(const('QQ_AUTO_LOCAL_FAST_SEED_MAX_AGE_MS')+100)
assert not h._qq_rebase_auto_local_from_coherent_uia(ui,'playing')
assert h._qq_auto_local_wait_seed

print('QQ FAST PROVISIONAL ANCHOR REPLAY: PASS')
print('  no fabricated 0s render clock before QQ seed: PASS')
print('  duration-matched validated playing pair seeds display-only clock immediately: PASS')
print('  paused manual bootstrap rejects rail hover but accepts off-rail pair: PASS')
print('  wrong duration cannot seed provisional display: PASS')
print('  stale late seed is rejected: PASS')
