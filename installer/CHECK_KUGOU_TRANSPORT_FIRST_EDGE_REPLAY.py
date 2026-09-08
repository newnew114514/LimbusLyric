#!/usr/bin/env python3
import ast, sys, textwrap
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_KUGOU_TRANSPORT_FIRST_EDGE_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)

def fail(msg):
    print('KUGOU TRANSPORT-FIRST EDGE REPLAY: FAIL'); print('  -',msg); raise SystemExit(1)

def fn(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name==name:
                    return ast.get_source_segment(src,m)
    fail(f'missing {cls}.{name}')

# Static integration gates.
for name in ('_kugou_on_gsmtc_edge','_kugou_publish_transport_edge','_kugou_attach_gsmtc_edge_session',
             '_kugou_flush_pending_media_transport_edge','request_kugou_transport_instance_from_edge',
             '_kugou_apply_pending_transport_instance'):
    fn('MediaSessionSync',name)
attach=fn('MediaSessionSync','_kugou_attach_gsmtc_edge_session')
for needle in ("('media', 'media_properties_changed')", "('timeline', 'timeline_properties_changed')", "('playback', 'playback_info_changed')", "f'add_{event_name}'", 'authority=evidence-only'):
    if needle not in attach: fail(f'event subscription missing {needle}')
poll=fn('MediaSessionSync','_poll_loop')
for needle in ('_kugou_attach_gsmtc_edge_session(session, source)','_kugou_flush_pending_media_transport_edge()', '_kugou_apply_pending_transport_instance()'):
    if needle not in poll: fail(f'poll integration missing {needle}')
bind=fn('MediaSessionSync','bind_track')
for needle in ('KUGOU_TRANSPORT_IDENTITY_EDGE_TTL_MS','_kg_previous_running',"_kg_status == 'playing'","_kg_reason = 'identity-transport-local'",'_kugou_transport_local_force_playing = True','trigger=confirmed-transport-identity'):
    if needle not in bind: fail(f'different-track transport-first bind missing {needle}')
rail=fn('MediaSessionSync','_kugou_rail_local_position')
if "in ('transport-edge-local', 'identity-transport-local')" not in rail or "effective = 'playing'" not in rail:
    fail('transport local rail does not resist stale hidden paused status')
consumer=fn('ControlPanel','_consume_kugou_transport_edge_fast')
for needle in ('KUGOU_TRANSPORT_STRONG_ARBITRATION_MS','KUGOU_TRANSPORT_FALLBACK_ARBITRATION_MS','_same_track(media_title, media_artist','request_kugou_transport_instance_from_edge','_kugou_pending_lyric_restart_serial'):
    if needle not in consumer: fail(f'same-track arbiter missing {needle}')
ack=fn('ControlPanel','_consume_kugou_transport_apply_ack')
for needle in ('kugou_transport_reset_applied_serial','self.lyric_window.stop_lyric()','_launch_current_lyrics(start_delay=0)','after-mediasync-ack=1'):
    if needle not in ack: fail(f'apply-ack visual restart missing {needle}')
bg=fn('ControlPanel','_consume_background_identity_fast')
if bg.find('_promote_kugou_background_identity_hint(') > bg.find('_consume_kugou_transport_edge_fast('):
    fail('same-track edge is still consumed before different-track identity promotion')

# Dynamic edge burst: current media event can publish only once; next media event re-arms.
edge_src='class Harness:\n'+textwrap.indent(fn('MediaSessionSync','_kugou_publish_transport_edge'),'    ')+'\n'+textwrap.indent(fn('MediaSessionSync','_kugou_on_gsmtc_edge'),'    ')+'\n'+'''\n    @staticmethod\n    def _process_stem(v): return str(v or '').lower()\n    def _set_state(self, **kw): self.state.update(kw)\n    @staticmethod\n    def _status_name(v): return str(v or 'unknown')\n'''
class Clock:
    now=10.0
    @classmethod
    def monotonic(cls): return cls.now
logs=[]
ns={'time':Clock,'write_error_log':lambda *a,**k: logs.append((a,k)),'KUGOU_TRANSPORT_STRONG_SETTLE_MS':900.0}
exec(edge_src,ns); h=ns['Harness'](); h._process_hint='kgmusic'; h._track_key='same|artist'; h.state={}
h._kugou_edge_media_mono=0; h._kugou_edge_media_track_key=''; h._kugou_edge_media_published_mono=0
h._kugou_edge_timeline_mono=0; h._kugou_edge_playback_mono=0; h._kugou_edge_playback_status='unknown'
h._kugou_transport_edge_serial=0; h._kugou_transport_edge_mono=0; h._kugou_transport_edge_reason=''; h._kugou_transport_edge_last_emit_mono=0
h._kugou_transport_local_force_playing=False; h._kugou_transport_local_started_mono=0; h._kugou_edge_diag_mono=0
Clock.now=10.000; h._kugou_on_gsmtc_edge('media')
if h._kugou_transport_edge_serial != 0: fail('media-only emitted transport before fallback window')
Clock.now=10.120; h._kugou_on_gsmtc_edge('timeline')
if h._kugou_transport_edge_serial != 1: fail('media+timeline burst did not emit serial 1')
Clock.now=10.700; h._kugou_on_gsmtc_edge('playback')
if h._kugou_transport_edge_serial != 1: fail('same media event published more than one transport serial')
Clock.now=11.000; h._kugou_on_gsmtc_edge('media')
Clock.now=11.130; h._kugou_on_gsmtc_edge('timeline')
if h._kugou_transport_edge_serial != 2: fail('repeated same-song transport did not re-arm on a new media event')
if h.state.get('kugou_transport_edge_serial') != 2: fail('transport serial not published into snapshot state')

# Dynamic media-only fallback: only unchanged track key can promote, and only once.
flush_src='class FlushHarness:\n'+textwrap.indent(fn('MediaSessionSync','_kugou_flush_pending_media_transport_edge'),'    ')+'''\n    @staticmethod\n    def _process_stem(v): return str(v or '').lower()\n    def _kugou_publish_transport_edge(self, reason, now): self.calls.append((reason,now)); self._kugou_edge_media_published_mono=self._kugou_edge_media_mono; return 1\n'''
ns={'time':Clock,'KUGOU_TRANSPORT_MEDIA_ONLY_MIN_AGE_MS':300.0}; exec(flush_src,ns); f=ns['FlushHarness'](); f._process_hint='kgmusic'; f.calls=[]
f._track_key='same|artist'; f._track_bound_mono=1000; f._kugou_edge_media_track_key='same|artist'; f._kugou_edge_media_mono=3000; f._kugou_edge_media_published_mono=0; f._kugou_edge_strong_settle_until_mono=0
Clock.now=3.5
if not f._kugou_flush_pending_media_transport_edge() or len(f.calls)!=1: fail('same-key media-only fallback did not promote')
if f._kugou_flush_pending_media_transport_edge() or len(f.calls)!=1: fail('same media-only event promoted twice')
f2=ns['FlushHarness'](); f2._process_hint='kgmusic'; f2.calls=[]; f2._track_key='new|artist'; f2._track_bound_mono=1000
f2._kugou_edge_media_track_key='old|artist'; f2._kugou_edge_media_mono=3000; f2._kugou_edge_media_published_mono=0; f2._kugou_edge_strong_settle_until_mono=0
Clock.now=3.5
if f2._kugou_flush_pending_media_transport_edge() or f2.calls: fail('different-key media event leaked into same-track fallback')

# H5: a post-burst duplicate media callback must be settled, not promoted as a second serial.
f3=ns['FlushHarness'](); f3._process_hint='kgmusic'; f3.calls=[]; f3._track_key='same|artist'; f3._track_bound_mono=1000
f3._kugou_edge_media_track_key='same|artist'; f3._kugou_edge_media_mono=3600; f3._kugou_edge_media_published_mono=3000; f3._kugou_edge_strong_settle_until_mono=3700
Clock.now=4.0
if f3._kugou_flush_pending_media_transport_edge() or f3.calls: fail('settled strong-burst media tail created a duplicate fallback serial')
if f3._kugou_edge_media_published_mono != 3600: fail('settled media tail was not marked consumed')

print('KUGOU TRANSPORT-FIRST EDGE REPLAY: PASS')
print('  different-track identity gets first refusal; playing is transport-evidence gated: PASS')
print('  each media event publishes at most one transport serial: PASS')
print('  same-track reset is applied on MediaSync thread and visuals restart after ACK: PASS')
print('  media-only fallback remains identity-restricted and one-shot: PASS')
print('  strong-burst media tail is settled instead of double-resetting: PASS')
