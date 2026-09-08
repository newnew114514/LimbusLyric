from pathlib import Path
import ast, sys, time

if len(sys.argv) != 2:
    raise SystemExit(2)
source_path = Path(sys.argv[1])
text = source_path.read_text(encoding='utf-8')

def need(cond, msg):
    if not cond:
        print('KUGOU VISUAL AUTHORITY + NETEASE BOOTSTRAP H36 REPLAY: FAIL')
        print(' - ' + msg)
        raise SystemExit(1)

markers = [
    '+ KUGOU VISUAL AUTHORITY + NETEASE BOOTSTRAP H36',
    'H36酷狗视觉大跳独立证据阻断',
    'H36网易云首个可信UIA显示先行',
    'H36网易云弱UIA连续钟确认',
    "NETEASE_NATIVE_IMPORT_MODE = 'sibling-file'",
    "MediaSessionSync._kugou_seed_rail_local_master._limbus_visual_authority = 'large-drift-requires-independent-authority'",
    "MediaSessionSync._merge_uia_position._limbus_ncm_unknown_status = 'sparse-doc-continuity'",
]
for marker in markers:
    need(marker in text, 'missing H36 marker: ' + marker)
need("if not sync._kugou_seed_rail_local_master(pos,status=status,reason='visual-rail-auto'" in text,
     'H34 visual layer does not honor lower-layer seed veto')
need("Path(__file__).resolve().with_name('limbus_netease_native.py')" in text,
     'NetEase sibling-file import fallback is missing')

# Extract pure policy helpers.
tree = ast.parse(text)
wanted_assign = {
    'H36_KUGOU_VISUAL_HARD_DRIFT_MIN_MS', 'H36_KUGOU_VISUAL_HARD_DRIFT_RATIO',
    'H36_NCM_DOC_PROGRESS_MIN_GAP_MS', 'H36_NCM_DOC_PROGRESS_MAX_GAP_MS',
}
wanted_funcs = {
    '_h36_kugou_visual_should_block', '_h36_ncm_doc_progress_coherent', '_h36_activate_runtime'
}
nodes=[]
for node in tree.body:
    if isinstance(node, ast.Assign):
        names={t.id for t in node.targets if isinstance(t, ast.Name)}
        if names & wanted_assign:
            nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in wanted_funcs:
        nodes.append(node)
ns={'time':time}
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source_path),'exec'),ns)
need(wanted_assign <= set(ns), 'failed to extract H36 constants')

kg=ns['_h36_kugou_visual_should_block']
need(kg(True, 87117, 49042, 251000), 'observed 38s KuGou visual rollback is not blocked')
need(not kg(True, 87117, 86600, 251000), 'small KuGou visual correction was over-blocked')
need(not kg(False, 1000, 40000, 251000), 'unanchored/provisional KuGou acquisition was incorrectly blocked')

ncm=ns['_h36_ncm_doc_progress_coherent']
need(ncm(34000, 42000, 8000), 'sparse 34s->42s NetEase natural progress was rejected')
need(not ncm(34000, 82000, 2000), '48s NetEase seek-like jump was incorrectly treated as continuity')
need(not ncm(34000, 34000, 8000), 'stale repeated NetEase doc clock incorrectly proved playback')

# Minimal runtime installation and KuGou seed-veto smoke.
class MS:
    def _kugou_seed_rail_local_master(self, position_ms, status='unknown', reason='bootstrap', absolute=False, now_ms=None):
        self.base_seed_calls = getattr(self, 'base_seed_calls', 0) + 1
        self.base_seed_value = position_ms
        return True
    def _kugou_poll_visual_rail_anchor(self, status_hint='unknown', local_position_hint=None):
        return self._kugou_seed_rail_local_master(49042, status='playing', reason='visual-rail-auto', absolute=True, now_ms=time.monotonic()*1000.0)
    def _merge_uia_position(self, process_name, status, fallback_position, fallback_trusted=False):
        return None, {}
    def _guard_auto_local_handoff(self, ui_position_ms, ui, status):
        return False, 610.0
    def _process_stem(self, value):
        return 'cloudmusic' if 'cloudmusic' in str(value).lower() else 'kgmusic'

ns.update({'MediaSessionSync':MS, 'write_error_log':lambda *a,**k:None})
ns['_h36_activate_runtime'].__globals__.update(ns)
ns['_h36_activate_runtime']()
need(getattr(MS._kugou_seed_rail_local_master, '_limbus_layer', '') == 'H36', 'H36 KuGou wrapper not installed')
need(getattr(MS._merge_uia_position, '_limbus_layer', '') == 'H36', 'H36 NetEase merge wrapper not installed')

m=MS()
now=time.monotonic()*1000.0
m._kugou_rail_master_active=True
m._kugou_rail_master_absolute=True
m._kugou_rail_master_position_ms=87117.0
m._kugou_rail_master_anchor_mono=now
m._kugou_rail_master_status='paused'
m._kugou_rail_master_reason='host-uia-range-v2'
m._kugou_rail_master_track_key='song|artist'
m._track_key='song|artist'
m._kugou_rail_master_player_epoch=3
m._media_player_epoch=3
m._kugou_rail_master_identity_epoch=9
m._track_identity_epoch=9
m._uia_duration_ms=251000
m._state={'duration_ms':251000}
blocked=MS._kugou_seed_rail_local_master(m,49042,status='playing',reason='visual-rail-auto',absolute=True,now_ms=now)
need(blocked is False and getattr(m,'base_seed_calls',0)==0, 'large visual rollback reached the base KuGou seed')
allowed=MS._kugou_seed_rail_local_master(m,86600,status='playing',reason='visual-rail-auto',absolute=True,now_ms=now)
need(allowed is True and getattr(m,'base_seed_calls',0)==1, 'small visual correction did not reach base KuGou seed')

print('KUGOU VISUAL AUTHORITY + NETEASE BOOTSTRAP H36 REPLAY: PASS')
print(' - established absolute KuGou clocks reject large visual-only rollbacks')
print(' - small visual corrections and unanchored acquisition remain available')
print(' - NetEase 34s->42s sparse doc samples prove continuity, while a 34s->82s jump does not')
print(' - H36 runtime wrappers are installed after the H35 stack')
