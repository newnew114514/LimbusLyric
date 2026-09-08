from pathlib import Path
import ast, sys, textwrap, time

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_BLUR_RELEASE_KUGOU_RESTART_H63_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H63 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ BLUR DECAY RELEASE + KUGOU RESTART DISPLAY H63','build tag')
need("if '_h63_activate_runtime' in globals():",'final activation')
if not (src.rindex("if '_h62_activate_runtime' in globals():") < src.rindex("if '_h63_activate_runtime' in globals():")):
    fail('H63 must activate after H62')

# Field symptom #1: a fallback draw is still a visible release frame. H62 used to return
# before incrementing the release draw counter, permanently pinning progress to 120ms.
draw=fsrc('h63_fading_draw')
for tok in (
    'result = draw_pre(row, painter)',
    "effect == H62_EXIT_EFFECT_BLUR_DECAY",
    "'_h62_decay_release_draw_count'",
    'before_release + 1',
    "write_error_log('H63渐进失焦退场首帧确认'",
):
    if tok not in draw: fail('fallback first-frame accounting missing '+tok)
# Run the nested wrapper with a fallback renderer that does not touch H62 counters.
ns={'H62_EXIT_EFFECT_BLUR_DECAY':'blur_decay','write_error_log':lambda *a,**k:None}
class Row: pass
r=Row(); r.exit_effect='blur_decay'; r._h62_decay_draw_count=0; r._h62_decay_release_draw_count=0; r._h62_decay_release_mono=1000.0
ns['draw_pre']=lambda row,painter:'fallback-painted'
exec(draw,ns)
out=ns['h63_fading_draw'](r,None)
if out!='fallback-painted' or r._h62_decay_draw_count!=1 or r._h62_decay_release_draw_count!=1:
    fail(f'fallback visible-frame replay failed: out={out!r} draw={r._h62_decay_draw_count} release={r._h62_decay_release_draw_count}')
# If H62 composite already counted the frame, H63 must not double count.
r2=Row(); r2.exit_effect='blur_decay'; r2._h62_decay_draw_count=4; r2._h62_decay_release_draw_count=3; r2._h62_decay_release_mono=1000.0
def counted(row,painter):
    row._h62_decay_draw_count += 1; row._h62_decay_release_draw_count += 1; return 'composite'
ns2=dict(ns); ns2['draw_pre']=counted; exec(draw,ns2)
ns2['h63_fading_draw'](r2,None)
if r2._h62_decay_draw_count!=5 or r2._h62_decay_release_draw_count!=4:
    fail('H63 double-counted H62 composite draw')

# H62 progress must be able to finish once that fallback frame is counted.
progress=fsrc('_h62_decay_progress'); smooth=fsrc('_h62_smoothstep')
ns3={'time':time,'H59_EXIT_FIRST_FRAME_CATCHUP_MS':120.0}
exec(smooth,ns3)
ns3['_h62_decay_durations']=lambda row:(10000.0,2000.0)
exec(progress,ns3)
r3=Row(); r3._h62_decay_release_mono=1000.0; r3._h62_decay_release_progress=0.0; r3._h62_decay_release_draw_count=0; r3._h62_decay_hold_mono=1.0
p0=ns3['_h62_decay_progress'](r3,6000.0)
r3._h62_decay_release_draw_count=1
p1=ns3['_h62_decay_progress'](r3,6000.0)
if not (p0<0.10 and p1>0.999): fail(f'H62 release does not unlock after visible fallback frame: {p0}->{p1}')

# Any row already in fading_lines is by definition in release phase, even if a legacy producer
# appended it directly without begin_fade().
adopt=fsrc('_h63_blur_decay_release_row')
for tok in ('row.begin_fade()', "reason='fading-membership'", "write_error_log('H63渐进失焦退场释放接管'"):
    if tok not in (adopt + '\n' + fsrc('h63_update_fading')): fail('fading membership adoption missing '+tok)
class DirectRow:
    exit_effect='blur_decay'; _h62_decay_release_mono=0.0; _h62_owner_ref=None
    def __init__(self): self.calls=0
    def begin_fade(self): self.calls+=1; self._h62_decay_release_mono=1234.0
ns4={'H62_EXIT_EFFECT_BLUR_DECAY':'blur_decay','_h62_weakref':__import__('weakref'),'write_error_log':lambda *a,**k:None}
exec(adopt,ns4)
d=DirectRow()
if not ns4['_h63_blur_decay_release_row'](d,None) or d.calls!=1 or d._h62_decay_release_mono<=0:
    fail('direct-appended fading row was not promoted to release phase')
if ns4['_h63_blur_decay_release_row'](d,None) or d.calls!=1:
    fail('release adoption is not idempotent')

# Field symptom #2 from the H51 frozen KuGou log: same Hero payload stayed loaded, visual rail was
# ~198.8s, but a recent HostV2 Slider candidate was already ~7.37s before the user clicked Start.
# H63 may use only that cached evidence for display re-anchor; it must not grant seek/duration.
helper=fsrc('_h63_kugou_user_start_pending_reanchor')
for tok in (
    "panel.player_combo.currentText() or '') != '酷狗音乐'",
    "'_kugou_host_v2_progress_pending'",
    "'_kugou_rail_master_position_ms'",
    'H63_KUGOU_START_PENDING_MAX_AGE_MS',
    'H63_KUGOU_START_BACKWARD_MIN_MS',
    "reason='h63-user-start-host-pending'",
    'absolute=False',
    "write_error_log('H63酷狗同曲重新开始展示预锚'",
    'duration-authority=unchanged | seek-authority=0',
):
    if tok not in helper: fail('KuGou restart display guard missing '+tok)
for bad in ('_set_state(', '_uia_duration_ms =', '_seek_serial =', 'bind_track(', '_track_key ='):
    if bad in helper: fail('KuGou restart helper crossed display-only boundary: '+bad)

class Combo:
    def currentText(self): return '酷狗音乐'
class LW: pass
class Sync:
    def __init__(self, now):
        self._process_hint='kgmusic.exe'; self._track_key='hero|mili'; self._track_identity_player_epoch=7; self._media_player_epoch=7
        self._kugou_host_v2_progress_pending={'source_key':'uia-range:Slider:x:y:(1,2,3,4)','last':7370.0,'last_mono':now-100.0,'count':1}
        self._kugou_rail_master_active=True; self._kugou_rail_master_position_ms=198800.0; self._kugou_rail_master_anchor_mono=now
        self._kugou_rail_master_status='playing'; self._uia_duration_ms=209000.0; self._state={'duration_ms':209000}
        self.seeded=None
    def _process_stem(self,p): return 'kgmusic'
    def _kugou_seed_rail_local_master(self,pos,**kw): self.seeded=(pos,kw); self._kugou_rail_master_position_ms=pos; return True
class Panel:
    pass
now=time.monotonic()*1000.0
panel=Panel(); panel.player_combo=Combo(); panel._loaded_track_key='hero|mili'; panel.media_sync=Sync(now); panel.lyric_window=LW()
ns5={'time':time,'H63_KUGOU_START_PENDING_MAX_AGE_MS':1800.0,'H63_KUGOU_START_BACKWARD_MIN_MS':8000.0,
     'H63_KUGOU_START_BACKWARD_DURATION_RATIO':0.035,'write_error_log':lambda *a,**k:None}
exec(helper,ns5)
if not ns5['_h63_kugou_user_start_pending_reanchor'](panel): fail('field Hero restart replay was not repaired')
if not panel.media_sync.seeded or abs(panel.media_sync.seeded[0]-7370.0)>0.1 or panel.media_sync.seeded[1].get('absolute') is not False:
    fail('Hero restart did not use pending HostV2 sample as display-only seed')
# Track mismatch and stale evidence must fail closed.
panel2=Panel(); panel2.player_combo=Combo(); panel2._loaded_track_key='other|mili'; panel2.media_sync=Sync(now); panel2.lyric_window=LW()
if ns5['_h63_kugou_user_start_pending_reanchor'](panel2): fail('track mismatch was allowed to re-anchor')
panel3=Panel(); panel3.player_combo=Combo(); panel3._loaded_track_key='hero|mili'; panel3.media_sync=Sync(now); panel3.media_sync._kugou_host_v2_progress_pending['last_mono']=now-5000; panel3.lyric_window=LW()
if ns5['_h63_kugou_user_start_pending_reanchor'](panel3): fail('stale HostV2 evidence was allowed to re-anchor')

# H63 is outer presentation/display closure only; do not monkeypatch core MediaSessionSync methods.
block=src[src.index('# H63 blur-decay release + KuGou same-track restart display closure'):]
block=block[:block.index('# H61 removes row-Atlas work from paint')]
if 'MediaSessionSync.' in block: fail('H63 monkeypatches protected MediaSessionSync core')
for tok in ('FadingLine.draw = h63_fading_draw','LyricWindow.update_fading = h63_update_fading','ControlPanel.start = h63_start'):
    if tok not in block: fail('H63 runtime owner missing '+tok)

print('BLUR RELEASE + KUGOU RESTART DISPLAY H63 REPLAY: PASS')
print(' - a visibly drawn H62 fallback frame releases the 120ms first-frame clamp instead of pinning fading rows forever')
print(' - every blur-decay row already in fading_lines is canonicalized into release phase')
print(' - explicit KuGou Start may use only a fresh same-track HostV2 candidate to repair a large stale display-clock rewind')
print(' - KuGou restart repair remains display-only: no seek, duration, track, or MediaSessionSync ownership mutation')
