from pathlib import Path
import ast, sys, textwrap, time, weakref

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_CAPACITY_AWARE_BLUR_DECAY_H64_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H64 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ CAPACITY-AWARE BLUR DECAY H64','build tag')
need("if '_h64_activate_runtime' in globals():",'final activation')
if not (src.rindex("if '_h63_activate_runtime' in globals():") < src.rindex("if '_h64_activate_runtime' in globals():")):
    fail('H64 must activate after H63')

helper=fsrc('_h64_capacity_aware_decay_progress')
for tok in (
    "'_h62_decay_release_mono'",
    'H64_BLUR_FILL_SPEED_MIN',
    'H64_BLUR_ACTIVE_PARK_PROGRESS',
    'not current_present',
    'float(live_count) / float(max(1, capacity))',
    "row._h64_capacity_target = int(capacity)",
):
    if tok not in helper: fail('capacity-aware progress missing '+tok)

state_src=fsrc('_h64_blur_residency_state')
for tok in ('max_visible_subtitles', 'history_lines', 'full_text', 'live_count'):
    if tok not in state_src: fail('residency state missing '+tok)

# Synthetic field replay. Same row age at 12s: a sparse 2/6 stack must blur slower than 5/6,
# neither may self-retire while a live lyric exists. Idle/instrumental must restore original H62 age retirement.
ns={
    'time':time,
    'H62_EXIT_EFFECT_BLUR_DECAY':'blur_decay',
    'H64_BLUR_FILL_SPEED_MIN':0.34,
    'H64_BLUR_ACTIVE_PARK_PROGRESS':0.88,
}
class Row: pass
class Win: pass
r=Row(); r.exit_effect='blur_decay'; r._h62_decay_release_mono=0.0; r._h62_decay_hold_mono=1000.0
w=Win(); w.max_visible_subtitles=6; w.full_text='current lyric'; w.history_lines=[r]
r._h62_owner_ref=weakref.ref(w)
ns['_h64_h62_decay_progress_pre']=lambda row,now_mono=None: min(1.0,max(0.0,(float(now_mono)-1000.0)/10000.0))
ns['_h62_decay_durations']=lambda row:(10000.0,2000.0)
exec(state_src,ns); exec(helper,ns)
p_sparse=ns['_h64_capacity_aware_decay_progress'](r,13000.0)
w.history_lines=[r,object(),object(),object()] # current + four history = 5/6
p_near=ns['_h64_capacity_aware_decay_progress'](r,13000.0)
if not (0.0 < p_sparse < p_near <= 0.88):
    fail(f'capacity speed replay wrong sparse={p_sparse:.3f} near={p_near:.3f}')
# Even very old history cannot vanish by age during active lyric flow; capacity overflow owns release.
p_old=ns['_h64_capacity_aware_decay_progress'](r,61000.0)
if p_old > 0.880001: fail(f'active capacity park failed: {p_old}')
# In an instrumental/provider-idle gap, original H62 clock must be restored and may reach invisible.
w.full_text=''
p_idle=ns['_h64_capacity_aware_decay_progress'](r,13000.0)
if p_idle < 0.999: fail(f'idle natural retirement was incorrectly held: {p_idle}')
# Once capacity already moved a row to release, H64 must leave H63/H62 release timing untouched.
w.full_text='current lyric'; r._h62_decay_release_mono=5000.0
p_release=ns['_h64_capacity_aware_decay_progress'](r,13000.0)
if p_release < 0.999: fail(f'release phase was stretched by H64: {p_release}')
# Capacity 1 retains historical behavior.
r._h62_decay_release_mono=0.0; w.max_visible_subtitles=1; w.full_text='current lyric'
p_one=ns['_h64_capacity_aware_decay_progress'](r,13000.0)
if p_one < 0.999: fail(f'capacity=1 behavior unexpectedly slowed: {p_one}')

# H64 must not alter normal exits, capacity manager, or core media ownership.
block=src[src.index('# H64 capacity-aware blur-decay residency'):]
# Later visual generations intentionally hook FadingLine/runtime methods. H64 owns only the
# section before H65, so its ownership audit must not attribute H65+ hooks back to H64.
if '# H65 continuous blur lifecycle + perceptual exit curve' in block:
    block=block[:block.index('# H65 continuous blur lifecycle + perceptual exit curve')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync.', '_release_history_lines =', '_enforce_visual_stack_limit =', 'FadingLine.begin_fade ='):
    if bad in block: fail('H64 crossed ownership boundary: '+bad)

print('CAPACITY-AWARE BLUR DECAY H64 REPLAY: PASS')
print(' - active lyric flow treats visible subtitle count as a soft residency target for blur-decay')
print(' - sparse stacks blur more slowly; age alone cannot retire rows before capacity overflow')
print(' - instrumental/provider-idle gaps still use original H62 natural age dissolve')
print(' - release phase and all non-blur exit/capacity/media ownership remain unchanged')
