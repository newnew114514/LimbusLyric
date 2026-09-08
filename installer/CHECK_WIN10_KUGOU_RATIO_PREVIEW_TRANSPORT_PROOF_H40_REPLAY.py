from pathlib import Path
import ast, sys, time, math, types

if len(sys.argv) != 2:
    raise SystemExit(2)
source_path = Path(sys.argv[1])
text = source_path.read_text(encoding='utf-8')

def need(cond, msg):
    if not cond:
        print('WIN10 KUGOU RATIO PREVIEW + TRANSPORT PROOF H40 REPLAY: FAIL')
        print(' - ' + msg)
        raise SystemExit(1)

markers = [
    '+ WIN10 KUGOU RATIO PREVIEW + TRANSPORT PROOF H40',
    'H40酷狗Win10比例预览秒跟',
    'H40酷狗Win10同曲Transport等待物理零点',
    'H40酷狗Win10同曲Transport物理零点放行',
    'H40酷狗Win10新身份阻止旧事务回滚',
    "_limbus_unowned_policy = 'ratio-preview-no-legacy-gesture-stamp'",
    "_limbus_same_track_reset = 'physical-near-zero-required-win10'",
]
for marker in markers:
    need(marker in text, 'missing H40 marker: ' + marker)

# Pure helpers: prove presentation ratio math and the same-identity reset rule.
tree = ast.parse(text)
wanted_assign = {
    'H38_KUGOU_VISUAL_DURATION_MIN_MS', 'H38_KUGOU_VISUAL_DURATION_MAX_MS',
    'H40_KUGOU_RATIO_PREVIEW_TTL_MS', 'H40_KUGOU_HELD_TRANSPORT_TTL_MS',
    'H40_KUGOU_NEAR_ZERO_RATIO_MAX', 'H40_KUGOU_NEAR_ZERO_PROOF_MAX_AGE_MS',
    'H40_KUGOU_NEAR_ZERO_MIN_HITS', 'H40_KUGOU_IDENTITY_ROLLBACK_GUARD_MS',
    'H40_KUGOU_FRAGMENT_DURATION_MIN_ROWS', 'H40_KUGOU_FRAGMENT_DURATION_MIN_SPAN_MS',
    'H40_KUGOU_FRAGMENT_DURATION_REL_SPREAD', 'H40_KUGOU_FRAGMENT_DURATION_MAX_AGE_MS',
}
wanted_funcs = {
    '_h40_ratio_preview_target', '_h40_near_zero_proof_rows',
    '_h40_should_hold_same_identity_transport', '_h40_fragmented_visual_duration_consensus', '_h40_activate_runtime',
}
nodes=[]
for node in tree.body:
    if isinstance(node, ast.Assign):
        names={t.id for t in node.targets if isinstance(t, ast.Name)}
        if names & wanted_assign:
            nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in wanted_funcs:
        nodes.append(node)

# Minimal runtime stubs. This actually executes the H40 unowned-click wrapper rather than
# merely searching source text, specifically guarding against H39's hidden legacy stamp leak.
class MediaSessionSync:
    def _kugou_commit_gesture_seek(self, target, now=None, reason='rail-gesture'):
        self.old_commit_calls = getattr(self, 'old_commit_calls', 0) + 1
        self._kugou_last_gesture_mono = float(now or 0)
        return True
    def _kugou_sync_rail_gesture_anchor(self):
        self.legacy_sync_calls = getattr(self, 'legacy_sync_calls', 0) + 1
        return True
    def request_kugou_transport_instance_from_edge(self, edge_serial, reason='gsmtc-transport-edge'):
        self.old_request_calls = getattr(self, 'old_request_calls', 0) + 1
        return True
    def _kugou_apply_pending_transport_instance(self):
        self.old_apply_calls = getattr(self, 'old_apply_calls', 0) + 1
        return True
    def _kugou_poll_visual_rail_anchor(self, status_hint=None, local_position_hint=None):
        return False
    def _set_visual_seek_override(self, target_ms, source='', now_ms=None, ttl_ms=1400.0, preserve_live=False, status=None):
        self.preview = (float(target_ms), str(source), float(ttl_ms))
        self._visual_seek_override_source = str(source)
    def _clear_visual_seek_override(self):
        self.preview = None
        self._visual_seek_override_source = ''
    def _mark_seek_burst(self, target_ms, source='', now_ms=None, suppress_serial=False):
        self.seek_burst = (float(target_ms), str(source), bool(suppress_serial))
    def _set_state(self, **kw):
        self._state.update(kw)
    def _kugou_seed_rail_local_master(self, *a, **kw):
        self.seed_calls = getattr(self, 'seed_calls', 0) + 1
        return True

class ControlPanel:
    def _promote_kugou_background_identity_hint(self, *a, **kw): return True
    def _restore_qq_suspended_loaded_track(self, *a, **kw): return True

visual_state={'proofs':[]}
def _h30_visual_state(sync, provider): return visual_state
def _h30_reset_visual_state(st, track, preserve_geometry=False):
    st['proofs']=[]
def _h37_kugou_win10_safe(sync): return True
def _h38_kugou_owned_duration(sync): return int(getattr(sync,'owned',0) or 0)
def _h39_kugou_ratio_from_untrusted_target(target, duration):
    if not duration: return None
    return max(0.0,min(1.0,float(target)/float(duration)))
def _h38_accept_kugou_player_duration(sync, duration_ms, source='player-evidence', position_ratio=None, now_ms=None):
    sync.owned=int(duration_ms); return True
def write_error_log(*a, **kw): pass

ns=dict(
    time=time, math=math, MediaSessionSync=MediaSessionSync, ControlPanel=ControlPanel,
    _h30_visual_state=_h30_visual_state, _h30_reset_visual_state=_h30_reset_visual_state,
    _h37_kugou_win10_safe=_h37_kugou_win10_safe, _h38_kugou_owned_duration=_h38_kugou_owned_duration,
    _h39_kugou_ratio_from_untrusted_target=_h39_kugou_ratio_from_untrusted_target,
    _h38_accept_kugou_player_duration=_h38_accept_kugou_player_duration,
    write_error_log=write_error_log,
)
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source_path),'exec'),ns)

preview=ns['_h40_ratio_preview_target'](0.5,221000,0,False)
need(preview == 110500.0, 'ratio preview does not map the physical rail ratio onto the current lyric timeline')
need(ns['_h40_should_hold_same_identity_transport'](True,'gsmtc-same-identity-transport',False),
     'Win10 same-identity transport edge can still reset without physical near-zero proof')
need(not ns['_h40_should_hold_same_identity_transport'](True,'gsmtc-same-identity-transport',True),
     'physical near-zero proof cannot release a legitimate same-title replay')
need(not ns['_h40_should_hold_same_identity_transport'](False,'gsmtc-same-identity-transport',False),
     'Win11 was incorrectly placed under the H40 Win10 transport rule')
now=10000.0
need(ns['_h40_near_zero_proof_rows']([{'ratio':0.03,'last_mono':9500,'hits':2,'span':500}],now),
     'fresh physical near-zero proof was not recognized')
need(not ns['_h40_near_zero_proof_rows']([{'ratio':0.30,'last_mono':9500,'hits':3,'span':1200}],now),
     'mid-song visual proof was incorrectly treated as song-zero evidence')

# Low-FPS fragmented proof consensus: 221s candidate-scaled movement corresponding to a
# real ~242s duration should cancel the candidate scale and converge near 242s.
frag=ns['_h40_fragmented_visual_duration_consensus']
rows=[]
for i,(span,ratio) in enumerate([(1200,0.30),(1600,0.32),(2100,0.35)]):
    real=242000.0
    advance=221000.0*span/real
    rows.append({'hits':2,'span':span,'advance':advance,'last_mono':8000+i*700,'ratio':ratio})
fc=frag(221000,rows,10000)
need(fc is not None and abs(float(fc['duration_ms'])-242000.0)<1500.0,
     'fragmented 2-hit rail proofs did not recover a stable player duration consensus')
rows_bad=list(rows)+[{'hits':2,'span':1500,'advance':221000*1500/90000.0,'last_mono':9900,'ratio':0.4}]
fc2=frag(221000,rows_bad,10000)
need(fc2 is not None and abs(float(fc2['duration_ms'])-242000.0)<2000.0,
     'one inconsistent motion fragment poisoned the duration consensus')

# Execute the actual installed H40 wrapper.
ns['_h40_activate_runtime']()
s=MediaSessionSync()
s._uia_duration_ms=221000
s._state={'duration_ms':221000,'status':'playing'}
s._est_status='playing'
s._track_key='少女a|鏡音リン'
s._media_player_epoch=7
s._kugou_last_gesture_mono=1234.0
s.owned=0
ratio=0.69477
target=221000*ratio
out=MediaSessionSync._kugou_commit_gesture_seek(s,target,now=5000.0,reason='h37-win10-safe-click')
need(out is False, 'unowned Win10 click unexpectedly committed an absolute clock')
need(getattr(s,'old_commit_calls',0)==0, 'H40 fell through to the legacy/H39 formal commit while duration was unowned')
need(abs(float(s._kugou_last_gesture_mono)-1234.0)<1e-9,
     'unowned click stamped _kugou_last_gesture_mono and can resurrect the pre-seek estimator')
need(getattr(s,'preview',None) is not None and s.preview[1]=='h40-kugou-ratio-preview',
     'unowned click did not publish an instant presentation-only preview')
need(abs(s.preview[0]-target)<1.0, 'presentation preview lost the physical click ratio')
need(getattr(s,'seek_burst',None) is not None, 'presentation preview did not publish a renderer discontinuity')
need(MediaSessionSync._kugou_sync_rail_gesture_anchor(s) is False,
     'pending unowned gesture can still promote the stale estimator through legacy gesture sync')

# The same-title GSMTC edge must be held until an independent physical near-zero proof exists.
visual_state['proofs']=[]
need(MediaSessionSync.request_kugou_transport_instance_from_edge(s, 7, reason='gsmtc-same-identity-transport') is False,
     'same-title transport edge was not held without near-zero proof')
need(getattr(s,'old_request_calls',0)==0, 'held same-title edge still reached the legacy request path')
visual_state['proofs']=[{'ratio':0.025,'last_mono':time.monotonic()*1000.0,'hits':2,'span':450}]
need(MediaSessionSync.request_kugou_transport_instance_from_edge(s, 8, reason='gsmtc-same-identity-transport') is True,
     'fresh physical near-zero proof did not release the legacy request path')
need(getattr(s,'old_request_calls',0)==1, 'near-zero release did not call the underlying request exactly once')

# Once a player-owned duration arrives, the pending ratio becomes an absolute clock and
# the long presentation preview is retired.
visual_state['proofs']=[]
accept=ns['_h38_accept_kugou_player_duration']
need(accept(s,230000,source='gsmtc-timeline',position_ratio=None,now_ms=6200.0),
     'player-owned duration was not accepted through H40')
need(getattr(s,'seed_calls',0)>=1, 'accepted duration did not promote the pending gesture to the rail-local master')
need(getattr(s,'preview',None) is None, 'presentation-only preview was not retired after player-owned duration arrived')
need(getattr(s,'_h40_kugou_pending_ratio',None) is None, 'pending ratio survived formal player-duration promotion')

print('WIN10 KUGOU RATIO PREVIEW + TRANSPORT PROOF H40 REPLAY: PASS')
print(' - unowned Win10 rail click follows immediately through presentation-only ratio preview')
print(' - unowned click never stamps legacy absolute gesture authority or formal media commit')
print(' - same-title GSMTC reset requires fresh physical near-zero rail proof on Win10')
print(' - Win11 transport behavior remains outside H40')
