#!/usr/bin/env python3
import ast, sys, textwrap
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_KUGOU_TRANSPORT_PAUSE_AUTHORITY_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)

def fail(msg):
    print('KUGOU TRANSPORT PAUSE AUTHORITY REPLAY: FAIL'); print('  -',msg); raise SystemExit(1)

def fn(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name==name:
                    return ast.get_source_segment(src,m)
    fail(f'missing {cls}.{name}')

bind=fn('MediaSessionSync','bind_track')
for needle in ('KUGOU_TRANSPORT_IDENTITY_EDGE_TTL_MS','_kg_previous_running',"_kg_status == 'playing'",'酷狗新曲暂停态保持'):
    if needle not in bind: fail(f'paused new-track gate missing {needle}')
edge=fn('MediaSessionSync','_kugou_on_gsmtc_edge')
if "edge_status != 'paused'" not in edge: fail('paused playback edge can still publish same-track transport')
if '_kugou_transport_local_force_playing = False' in edge: fail('WinRT callback still mutates rail-local pause authority')
rail=fn('MediaSessionSync','_kugou_rail_local_position')
for needle in ('KUGOU_TRANSPORT_EXPLICIT_PAUSE_MIN_AGE_MS','酷狗Transport显式暂停冻结','advance_until = min','酷狗Transport显式恢复续时'):
    if needle not in rail: fail(f'rail-local pause/resume logic missing {needle}')
poll=fn('MediaSessionSync','_poll_loop')
if "status = str(getattr(self, '_kugou_rail_master_status', status) or status)" not in poll:
    fail('public status is not synchronized to the public KuGou local clock')

# Dynamic local transport: explicit pause freezes at edge time and a later explicit resume
# re-arms movement even if hidden GSMTC snapshots remain stale-paused.
rail_src='class Harness:\n'+textwrap.indent(rail,'    ')+'''\n    def _reset_kugou_rail_local_master(self): self._kugou_rail_master_active=False\n    def _kugou_poll_uia_progress_v2(self, *a, **k): return None\n    def _kugou_poll_visual_rail_anchor(self, *a, **k): return False\n    def _kugou_advance_transport_generation(self, *a, **k): return 0\n    def _kugou_seed_rail_local_master(self, *a, **k): return False\n'''
class Clock:
    now=3.2
    @classmethod
    def monotonic(cls): return cls.now

def continuation(pending, value, duration, status, now, **kw):
    return pending, False, ''
logs=[]
ns={
    'time':Clock,'re':__import__('re'),'write_error_log':lambda *a,**k: logs.append((a,k)),
    'KUGOU_RAIL_LOCAL_MASTER_ENABLED':True,'KUGOU_TRANSPORT_EXPLICIT_PAUSE_MIN_AGE_MS':260.0,
    'KUGOU_TRANSPORT_EXPLICIT_RESUME_GRACE_MS':1800.0,'KUGOU_RAIL_LOCAL_MASTER_LOG_SEC':9999.0,
    '_kugou_same_identity_end_continuation_step':continuation,
}
exec(rail_src,ns); h=ns['Harness']()
h._kugou_rail_master_active=True; h._kugou_rail_master_track_key='same|artist'; h._track_key='same|artist'
h._kugou_rail_master_player_epoch=1; h._media_player_epoch=1; h._kugou_rail_master_identity_epoch=1; h._track_identity_epoch=1
h._kugou_rail_master_anchor_mono=1000.0; h._kugou_rail_master_position_ms=0.0; h._kugou_rail_master_status='playing'
h._kugou_rail_master_absolute=False; h._kugou_rail_master_reason='transport-edge-local'; h._kugou_rail_master_last_diag_mono=0.0
h._kugou_auto_playing_carry_until_mono=0.0; h._kugou_host_motion_playing_until_mono=0.0; h._kugou_host_motion_playing_track_key=''
h._kugou_transport_local_force_playing=True; h._kugou_transport_local_started_mono=1000.0
h._kugou_transport_pause_applied_edge_mono=0.0; h._kugou_transport_resume_applied_edge_mono=0.0
h._kugou_edge_playback_mono=3000.0; h._kugou_edge_playback_status='paused'
h._uia_duration_ms=142000; h._state={'duration_ms':142000}; h._est_position_ms=0; h._est_anchor_mono=1000; h._est_status='playing'
h._kugou_host_v2_progress_trusted_key=''; h._kugou_host_v2_progress_last_success_mono=0.0; h._kugou_visual_last_anchor_mono=0.0
h._kugou_end_continuation_pending=None; h._kugou_visual_last_diag_mono=0.0
v=h._kugou_rail_local_position('paused')
if not (1990 <= v <= 2010): fail(f'explicit pause did not freeze at callback time: {v}')
if h._kugou_rail_master_status != 'paused' or h._kugou_transport_local_force_playing:
    fail('explicit pause did not retire force-playing lane')
Clock.now=8.0
v2=h._kugou_rail_local_position('paused')
if v2 != v: fail(f'paused local clock kept advancing: {v}->{v2}')
# Resume event at 8.1s; hidden snapshot is still stale paused.
h._kugou_edge_playback_mono=8100.0; h._kugou_edge_playback_status='playing'; Clock.now=8.2
v3=h._kugou_rail_local_position('paused')
if h._kugou_rail_master_status != 'playing' or not h._kugou_transport_local_force_playing:
    fail('explicit resume did not re-arm local movement')
Clock.now=9.2
v4=h._kugou_rail_local_position('paused')
if v4 < v3 + 900: fail(f'resumed local clock did not keep moving through stale paused snapshot: {v3}->{v4}')
print('KUGOU TRANSPORT PAUSE AUTHORITY REPLAY: PASS')
print('  paused new-track attach does not invent playback without transport evidence: PASS')
print('  paused playback callbacks cannot create same-song transport: PASS')
print('  explicit pause freezes local clock at callback time: PASS')
print('  explicit resume re-arms local movement through stale hidden snapshots: PASS')
print('  public monitor status follows the public KuGou local clock: PASS')
