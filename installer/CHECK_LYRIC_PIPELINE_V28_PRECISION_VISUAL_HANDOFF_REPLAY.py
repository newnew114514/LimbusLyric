#!/usr/bin/env python3
import ast, bisect, re, sys, textwrap
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V28_PRECISION_VISUAL_HANDOFF_REPLAY.py <main.py>')
p = Path(sys.argv[1]); src = p.read_text(encoding='utf-8'); tree = ast.parse(src)

def fail(msg):
    print('LYRIC PIPELINE V28 PRECISION VISUAL HANDOFF REPLAY: FAIL')
    print('  -', msg); raise SystemExit(1)

def fn(cls, name):
    for n in tree.body:
        if isinstance(n, ast.ClassDef) and n.name == cls:
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == name:
                    return ast.get_source_segment(src, m)
    fail(f'missing {cls}.{name}')

if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')):
    fail('V28+ marker missing')

upgrade = fn('LyricWindow', 'upgrade_lyric_timeline_preserve_visual')
activate = fn('LyricWindow', '_activate_precision_handoff')
check = fn('LyricWindow', 'check_lyric_time')
place = fn('LyricWindow', 'place_randomly')

for needle in (
    "old_char_index > 0", "_precision_handoff_pending = {", "matched_precise_line",
    "candidate_boundary > pos_i + 40", "精确歌词视觉租约建立",
):
    if needle not in upgrade:
        fail(f'visual lease creation missing: {needle}')
for needle in (
    "reason='boundary'", "reason) == 'seek'", "self.displayed_line_index = target - 1",
    "精确歌词视觉租约交接",
):
    if needle not in activate:
        fail(f'atomic handoff path missing: {needle}')
for needle in (
    "_row_complete", "_pending_target == _matched", "reason='row-complete'",
    "int(position_ms) >= int(_boundary) and _row_complete",
    "target = int(self.displayed_line_index)", "reason='seek'",
):
    if needle not in check:
        fail(f'lease enforcement missing from renderer tick: {needle}')
if "_apply_visual_reveal_state" not in check:
    fail('renderer reveal engine unexpectedly removed')
reveal = fn('LyricWindow', '_apply_visual_reveal_state')
for needle in ('_precision_handoff_visible_floor', '_raw_idx < _floor_chars', 'idx = _floor_chars'):
    if needle not in reveal:
        fail(f'completed-row no-retract floor missing: {needle}')

# V28 overlap follow-up must spend more candidate scores only in crowded scenes; effects/placement
# remain the same scorer and random spread model.
for needle in ('crowded_scene = len(obstacles) >= 3', '4 if crowded_scene else 3',
               '56 if crowded_scene else 28', 'pool={len(candidate_visuals)}'):
    if needle not in place:
        fail(f'crowded collision expansion missing: {needle}')

# Dynamically execute only the new handoff helpers/method with tiny stubs. This proves that an
# already-visible first line keeps the ordinary timeline until the precise boundary, while a seek
# or an as-yet-invisible row can adopt precision immediately.
method_names = ['_precision_handoff_text_key', '_activate_precision_handoff', 'upgrade_lyric_timeline_preserve_visual']
method_src = '\n'.join(textwrap.indent(fn('LyricWindow', name), '    ') for name in method_names)
class_src = 'class Harness:\n' + method_src + '''\n    def _schedule_song_fragment_atlas(self):\n        self.atlas_scheduled += 1\n    def _animation_frame_interval(self):\n        return 16\n    def update(self):\n        self.updates += 1\n'''

PRECISE = [
    (0, 'ABC', [(0,1,300),(300,2,600),(600,3,900)]),
    (5000, 'DEF', [(5000,1,5300),(5300,2,5600),(5600,3,5900)]),
    (9000, 'GHI', [(9000,1,9300),(9300,2,9600),(9600,3,9900)]),
]
ORDINARY = [(0, 'ABC', None), (4000, 'DEF', None), (8000, 'GHI', None)]

class Timer:
    def __init__(self): self.active=True; self.starts=[]
    def isActive(self): return self.active
    def start(self, ms): self.active=True; self.starts.append(ms)

def parse_lrc_stub(_): return list(PRECISE)
def log_stub(*a, **k): pass
ns = {
    're': re, 'bisect': bisect, 'parse_lrc': parse_lrc_stub, 'write_error_log': log_stub,
    'FLOW_STACK_ENABLED': True, 'SMOOTH_CLOCK_FLOW_ENABLED': True,
}
exec(class_src, ns)
Harness = ns['Harness']
Harness._precision_handoff_text_key = staticmethod(Harness._precision_handoff_text_key)

def make(chars=2, pos=2500):
    h=Harness(); h.lyric_timeline=list(ORDINARY); h._lyric_times=[0,4000,8000]
    h._rhythm_event_cache={}; h._adaptive_pace_cache={}; h._provider_cadence_cache=None; h._provider_local_cadence_cache={}
    h._has_precise_timing=False; h.full_text='ABC'; h.char_index=chars; h.displayed_line_index=0; h.current_line=1
    h.history_lines=[]; h.fading_lines=[]; h._last_position_ms=pos; h._precision_handoff_pending=None
    h.line_timer=Timer(); h.shake_timer=Timer(); h.atlas_scheduled=0; h.updates=0; h._precision_handoff_visible_floor=None
    return h

h=make(chars=2, pos=2500)
if not h.upgrade_lyric_timeline_preserve_visual('precise'):
    fail('visible-row upgrade returned false')
if h.lyric_timeline != ORDINARY:
    fail('visible row swapped to precise timeline immediately')
if not isinstance(h._precision_handoff_pending, dict):
    fail('visible row did not create pending precise lease')
if h._precision_handoff_pending.get('boundary_ms') != 5000:
    fail(f'expected next precise boundary 5000, got {h._precision_handoff_pending.get("boundary_ms")}')
if h.char_index != 2:
    fail('lease creation rewound/advanced visible glyph count')

# If the fallback row finishes before a long next-row boundary, a matched precise row may become
# the internal timeline immediately while a full-row visual floor prevents any precise tick from
# retracting already-seen glyphs.
h_early=make(chars=2, pos=2500); h_early.upgrade_lyric_timeline_preserve_visual('precise'); h_early.char_index=3
if not h_early._activate_precision_handoff(3200, reason='row-complete'):
    fail('row-complete activation failed')
if h_early.lyric_timeline != PRECISE or h_early.displayed_line_index != 0:
    fail('row-complete activation did not retain matched precise current row')
if not isinstance(h_early._precision_handoff_visible_floor, dict) or h_early._precision_handoff_visible_floor.get('chars') != 3:
    fail('row-complete activation did not install full-row visual floor')

# Once the row is complete and the safe precise boundary is reached, activation maps the old row
# to target-1 so the existing normal line-transition path can fade it exactly once.
h.char_index=3
if not h._activate_precision_handoff(5000, reason='boundary'):
    fail('boundary activation failed')
if h.lyric_timeline != PRECISE or h._precision_handoff_pending is not None:
    fail('boundary activation did not atomically install precise timeline')
if h.displayed_line_index != 0:  # target 1 => target-1
    fail(f'boundary activation did not preserve old row as immediate predecessor: {h.displayed_line_index}')

# An accepted seek explicitly invalidates continuity and must force precise rebuild now.
h=make(chars=2, pos=2500); h.upgrade_lyric_timeline_preserve_visual('precise')
if not h._activate_precision_handoff(2200, reason='seek'):
    fail('seek activation failed')
if h.lyric_timeline != PRECISE or h.displayed_line_index != -1:
    fail('seek did not force immediate precise rebuild state')

# If not a single glyph has been shown yet, there is no user-visible past to protect.
h=make(chars=0, pos=2500)
h.upgrade_lyric_timeline_preserve_visual('precise')
if h.lyric_timeline != PRECISE or h._precision_handoff_pending is not None:
    fail('invisible row did not adopt precision immediately')

print('LYRIC PIPELINE V28 PRECISION VISUAL HANDOFF REPLAY: PASS')
print('  visible fallback row retains its original timeline/cadence: PASS')
print('  matched completed row may adopt precision early with a no-retract floor: PASS')
print('  precise next-row boundary + row-complete gate: PASS')
print('  accepted seek bypasses presentation lease: PASS')
print('  zero-visible-glyph precision remains immediate: PASS')
print('  crowded predictive placement gets expanded candidate pool: PASS')
