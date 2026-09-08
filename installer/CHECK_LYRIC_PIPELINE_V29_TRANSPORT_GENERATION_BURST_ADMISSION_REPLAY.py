#!/usr/bin/env python3
import ast, hashlib, sys, textwrap, types
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V29_TRANSPORT_GENERATION_BURST_ADMISSION_REPLAY.py <main.py>')
p = Path(sys.argv[1]); src = p.read_text(encoding='utf-8'); tree = ast.parse(src)

def fail(msg):
    print('LYRIC PIPELINE V29 TRANSPORT GENERATION + BURST ADMISSION REPLAY: FAIL')
    print('  -', msg); raise SystemExit(1)

def top_fn(name):
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return ast.get_source_segment(src, n)
    fail(f'missing top-level {name}')

def fn(cls, name):
    for n in tree.body:
        if isinstance(n, ast.ClassDef) and n.name == cls:
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == name:
                    return ast.get_source_segment(src, m)
    fail(f'missing {cls}.{name}')

def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

if 'INSTRUMENTAL-RUNTIME-V29' not in src:
    fail('V29 marker missing')

# V28 presentation lease is frozen byte-for-byte: V29 may only solve transport generation,
# burst admission, atlas install latency diagnostics, and network timeout log hygiene.
frozen = {
    'upgrade_lyric_timeline_preserve_visual': 'f660f8d1a5324364726d795a0ee17af6b1aab8590eec5084201734ab2132cebe',
    '_activate_precision_handoff': '345c34d272ac26f1a38d8126c9cb8b2efb80a80f22f4eea9dbcd1972683d8995',
    '_apply_visual_reveal_state': '530790efc4381316ae817ae34e6564ff2720febea4b9b8015947c8061a6f9a64',
    '_precision_handoff_text_key': 'b792e00c3e278dac4564e86ee692949128ac4a6c09f10ed7ea5b26ef7b22326a',
}
for name, expected in frozen.items():
    actual = sha(fn('LyricWindow', name))
    if actual != expected:
        fail(f'V28 frozen renderer method changed: {name} {actual}')
# H8 moves only the atlas source-rectangle wrapper construction into the worker so a
# slow machine cannot spend hundreds of GUI milliseconds creating QRectF metadata. Freeze
# the entire V28 raster/packing algorithm after removing that one representation assignment.
def atlas_builder_without_meta_assignment(text):
    node = ast.parse(text).body[0]
    class StripMeta(ast.NodeTransformer):
        def visit_Assign(self, item):
            for target in item.targets:
                if (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)
                        and target.value.id == 'meta'):
                    return None
            return self.generic_visit(item)
    node = StripMeta().visit(node)
    ast.fix_missing_locations(node)
    return ast.unparse(node)
if sha(atlas_builder_without_meta_assignment(top_fn('_build_song_fragment_atlas_image'))) != '62d2f1bf239d8d446ef78043220210b9fc6819c94aa78ce0c3bb93c0398575ec':
    fail('V28 atlas raster/packing algorithm changed outside H8 metadata representation')

# ---- KuGou same-title hidden play-instance generation ----
helper = top_fn('_kugou_same_identity_end_continuation_step')
ns = {}
exec(helper, ns)
step = ns['_kugou_same_identity_end_continuation_step']

pending, restart, reason = step(None, 30000, 142000, 'playing', 0)
if pending is not None or restart or reason != 'not-at-end':
    fail('mid-song playing armed same-title rollover')
pending, restart, reason = step(None, 142000, 142000, 'paused', 0)
if pending is not None or restart:
    fail('paused end armed same-title rollover')
pending, restart, reason = step(None, 142000, 142000, 'playing', 0, host_clock_fresh=True)
if pending is not None or restart or reason != 'real-clock-present':
    fail('fresh Host-V2 clock did not veto hidden rollover inference')
pending, restart, _ = step(None, 142000, 142000, 'playing', 100)
if not isinstance(pending, dict) or restart:
    fail('hidden end did not arm continuation proof')
pending, restart, _ = step(pending, 142000, 142000, 'playing', 700)
if restart:
    fail('hidden end restarted before dwell proof')
pending, restart, reason = step(pending, 142000, 142000, 'playing', 1400)
if not restart or pending is not None or not str(reason).startswith('end-playing-dwell:'):
    fail('hidden same-title end continuation did not prove after 3 hits/1.25s')
pending, restart, reason = step({'first_mono':0,'last_mono':500,'duration_ms':142000,'hits':2,'position_ms':142000}, 130000, 142000, 'playing', 700)
if pending is not None or restart or reason != 'not-at-end':
    fail('leaving end boundary did not clear continuation proof')

rail = fn('MediaSessionSync', '_kugou_rail_local_position')
for needle in (
    'host_clock_fresh', 'visual_clock_fresh', '_kugou_same_identity_end_continuation_step(',
    "reason='same-title-play-instance-restart'", '酷狗同名播放实例末端续播回锚',
    '_kugou_advance_transport_generation(', 'inferred_position=', 'end-playing-dwell:', 'identity-reset=0', 'provider-restart=0',
):
    if needle not in rail:
        fail(f'KuGou hidden play-instance path missing: {needle}')
if '_request_auto_track' in rail:
    fail('KuGou hidden play-instance clock path unexpectedly restarts provider search')

host = fn('MediaSessionSync', '_kugou_poll_uia_progress_v2')
for needle in ('same_track_restart', '酷狗同曲重新播放时钟立即回锚', "'host-v2-position-collapse'", '_kugou_advance_transport_generation'):
    if needle not in host:
        fail(f'existing Host-V2 same-track restart proof/diagnostic lost: {needle}')

cold = fn('MediaSessionSync', '_kugou_cold_bootstrap_transport_probe')
for required in ('_kugou_poll_uia_progress_v2', '_kugou_poll_visual_rail_anchor', 'synthetic-zero=0', '_startup_existing_attach = False'):
    if required not in cold:
        fail(f'KuGou cold first-track rail bootstrap missing: {required}')
snapshot = fn('MediaSessionSync', '_poll_loop')
if '_kugou_cold_bootstrap_transport_probe(status, fallback_position_ms)' not in snapshot:
    fail('KuGou cold rail probe is not reachable before rail-local master exists')
if snapshot.find('_kugou_cold_bootstrap_transport_probe(status, fallback_position_ms)') > snapshot.find('_kugou_rail_local_position(status)'):
    fail('KuGou cold rail probe still runs after the rail-local-master dependency')

cold_class = 'class ColdHarness:\n' + textwrap.indent(cold, '    ') + '''\n    @staticmethod\n    def _process_stem(value):\n        return str(value or '').lower()\n'''
class ColdReader:
    def __init__(self): self.late=[]
    def set_startup_late_attach(self, value): self.late.append(bool(value))
cold_logs=[]
ns={'KUGOU_RAIL_LOCAL_MASTER_ENABLED':True,'write_error_log':lambda *a,**k:cold_logs.append((a,k))}
exec(cold_class,ns); ch=ns['ColdHarness'](); ch._process_hint='kgmusic'; ch._track_key='song|artist'
ch._kugou_rail_master_active=False; ch._startup_existing_attach=True; ch._uia_reader=ColdReader(); ch.visual_calls=0
def host_probe(status,local_position_hint=None):
    ch._kugou_rail_master_active=True; ch._kugou_rail_master_position_ms=1234.0; ch._kugou_rail_master_reason='host-uia-range-v2'; return 1234
def visual_probe(**kwargs): ch.visual_calls+=1; return False
ch._kugou_poll_uia_progress_v2=host_probe; ch._kugou_poll_visual_rail_anchor=visual_probe
if not ch._kugou_cold_bootstrap_transport_probe('paused',0):
    fail('KuGou cold Host-V2 bootstrap did not establish first-track rail')
if ch._startup_existing_attach or ch._uia_reader.late != [False] or ch.visual_calls != 0:
    fail('KuGou cold Host-V2 bootstrap did not retire late-attach cleanly')
ch2=ns['ColdHarness'](); ch2._process_hint='kgmusic'; ch2._track_key='song|artist'; ch2._kugou_rail_master_active=False
ch2._startup_existing_attach=True; ch2._uia_reader=ColdReader(); ch2.visual_calls=0
ch2._kugou_poll_uia_progress_v2=lambda *a,**k: None
def paused_visual(**kwargs): ch2.visual_calls+=1; return False
ch2._kugou_poll_visual_rail_anchor=paused_visual
if ch2._kugou_cold_bootstrap_transport_probe('paused',0) or ch2.visual_calls:
    fail('KuGou paused cold bootstrap used the screen-motion rail without playing proof')

advance = fn('MediaSessionSync', '_kugou_advance_transport_generation')
for needle in ('self._seek_serial', 'seek_serial=int(self._seek_serial)', '酷狗播放实例视觉断点已发布', 'provider-restart=0'):
    if needle not in advance:
        fail(f'KuGou transport generation does not publish the existing visual discontinuity serial: {needle}')
renderer = fn('LyricWindow', 'check_lyric_time')
if 'seek_like = bool(explicit_seek)' not in renderer:
    fail('source-locked renderer seek/discontinuity consumer changed unexpectedly')

# Dynamic generation replay: same-title next play instance publishes only a display
# discontinuity. Identity/provider generations are deliberately outside this helper.
advance_class = 'class TransportHarness:\n' + textwrap.indent(advance, '    ') + '''\n    def _set_state(self, **kwargs):\n        self.state.update(kwargs)\n'''
class GenTime:
    @staticmethod
    def monotonic(): return 12.5
gen_logs=[]
ns = {'time': GenTime, 'write_error_log': lambda *a, **k: gen_logs.append((a,k))}
exec(advance_class, ns); th = ns['TransportHarness']()
th._kugou_transport_generation=4; th._seek_serial=8; th._kugou_end_continuation_pending={'hits': 3}; th.state={}
if th._kugou_advance_transport_generation('replay', 0, 'same-title') != 5:
    fail('transport generation did not increment')
if th._seek_serial != 9 or th.state.get('seek_serial') != 9 or th.state.get('kugou_transport_generation') != 5:
    fail(f'transport generation did not publish visual serial/state: {th.state}')
if th._kugou_end_continuation_pending is not None:
    fail('transport generation did not retire the end-continuation proof')

# ---- KuGou zero-touch latency + cross-restart lyric cache ----
if 'KUGOU_ZERO_TOUCH_BOOTSTRAP_DELAY_MS' not in src or "LIMBUSLYRIC_KUGOU_ZERO_TOUCH_DELAY_MS', '120'" not in src:
    fail('KuGou-specific zero-touch startup delay missing/default changed')
selected_delay = fn('ControlPanel', '_selected_zero_touch_bootstrap_delay_ms')
for needle in ("currentText() == '酷狗音乐'", 'KUGOU_ZERO_TOUCH_BOOTSTRAP_DELAY_MS', 'BUILTIN_ZERO_TOUCH_BOOTSTRAP_DELAY_MS'):
    if needle not in selected_delay:
        fail(f'player-scoped zero-touch delay missing: {needle}')
if src.count('self._selected_zero_touch_bootstrap_delay_ms()') < 2:
    fail('startup/deferred zero-touch paths do not both use player-scoped delay')
for name in ('_load_auto_lyric_cache_from_disk', '_persist_auto_lyric_cache'):
    body = fn('ControlPanel', name)
    if 'AUTO_LYRIC_CACHE_FILE' not in body:
        fail(f'persistent auto lyric cache path missing from {name}')
load_cache = fn('ControlPanel', '_load_auto_lyric_cache_from_disk')
persist_cache = fn('ControlPanel', '_persist_auto_lyric_cache')
search_job = fn('ControlPanel', '_start_auto_search_job')
for needle in ('14 * 86400', "row.get('lyric')", 'tuple(raw_key)'):
    if needle not in load_cache:
        fail(f'persistent lyric cache load guard missing: {needle}')
for needle in ('os.replace(tmp, AUTO_LYRIC_CACHE_FILE)', "'saved_at'", "'version': 1"):
    if needle not in persist_cache:
        fail(f'persistent lyric cache atomic save missing: {needle}')
for needle in ("'saved_at': time.time()", 'self._persist_auto_lyric_cache()', 'fast_cached = cache_get(fast_key)'):
    if needle not in search_job:
        fail(f'auto-search does not consume/persist cross-restart cache: {needle}')

# ---- High-density admission must retire only already-fading exits ----
burst = fn('LyricWindow', '_pre_admit_burst_row')
for needle in ('gap_ms <= 760 and chars >= 20', 'gap_ms <= 1100 and chars >= 48',
               'gap_ms <= 1500 and chars >= 90', 'self.fading_lines', '_discard_fading_item',
               '高密度字幕入场前退场清障', 'history_preserved='):
    if needle not in burst:
        fail(f'burst admission control missing: {needle}')
for forbidden in ('self.history_lines =', 'self.history_lines.clear(', 'self.full_text =', 'self.font_size ='):
    if forbidden in burst:
        fail(f'burst admission changes readable content/style: {forbidden}')
check = fn('LyricWindow', 'check_lyric_time')
if '_pre_admit_burst_row(target)' not in check or check.find('_pre_admit_burst_row(target)') > check.find('_place_randomly_safe()'):
    fail('burst capacity control is not executed before placement')

# Dynamic burst replay: history is immutable, only fading exits are retired in extreme cadence.
class_src = 'class Harness:\n' + textwrap.indent(burst, '    ') + '''\n    def _placement_obstacles(self):\n        return list(self.history_lines) + list(self.fading_lines)\n    def _discard_fading_item(self, item):\n        self.discarded.append(item)\n'''
class FakeTime:
    @staticmethod
    def monotonic(): return 100.0
logs=[]
ns = {'time': FakeTime, 'write_error_log': lambda *a, **k: logs.append((a,k))}
exec(class_src, ns); Harness = ns['Harness']
h = Harness(); h.lyric_timeline=[(0,'x',None),(500,'y',None)]; h.full_text='X'*60
h.history_lines=['h1','h2']; h.fading_lines=['f1','f2','f3']; h.discarded=[]; h._last_burst_admission_log_mono=0
n=h._pre_admit_burst_row(0)
if n != 3 or h.history_lines != ['h1','h2'] or h.fading_lines or h.discarded != ['f1','f2','f3']:
    fail(f'burst admission did not retire only fading exits: n={n} history={h.history_lines} fading={h.fading_lines}')
h2=Harness(); h2.lyric_timeline=[(0,'x',None),(3000,'y',None)]; h2.full_text='X'*100
h2.history_lines=['h1','h2']; h2.fading_lines=['f1']; h2.discarded=[]; h2._last_burst_admission_log_mono=0
if h2._pre_admit_burst_row(0) != 0 or h2.fading_lines != ['f1']:
    fail('normal-cadence row triggered burst admission cleanup')

# ---- Atlas install: no quality change, stale result is dropped before QPixmap conversion,
# and install stages are observable. ----
install = fn('LyricWindow', '_install_song_fragment_atlas')
reserve = fn('LyricWindow', '_reserve_song_fragment_atlas_capacity')
for needle in ('_song_fragment_atlas_stale_drop_count', '_reserve_song_fragment_atlas_capacity',
               'QPixmap.fromImage(image)', '整曲字形Atlas安装诊断', 'convert=', 'meta=', 'evict=', 'activate='):
    if needle not in install:
        fail(f'atlas staged install missing: {needle}')
if install.find('_song_fragment_atlas_stale_drop_count') > install.find('QPixmap.fromImage(image)'):
    fail('stale atlas result is not rejected before QPixmap conversion')
for needle in ('SONG_FRAGMENT_ATLAS_CACHE_MAX_ENTRIES', 'SONG_FRAGMENT_ATLAS_CACHE_MAX_PIXELS', 'cache.keys()'):
    if needle not in reserve:
        fail(f'pre-conversion atlas capacity reserve missing: {needle}')
perf = fn('LyricWindow', '_record_paint_perf')
for needle in ('atlas_install=', 'atlas_evict=', 'atlas_stale_drop='):
    if needle not in perf:
        fail(f'atlas runtime telemetry missing from perf log: {needle}')

# ---- Expected network timeout is concise; unexpected provider exceptions keep traceback. ----
fail_src = fn('LyricSearchEngine', '_fail')
for needle in ('requests.exceptions.Timeout', '歌词搜索网络超时/', 'traceback=suppressed-expected-network-timeout',
               'write_error_log(f"歌词搜索失败/{source}", exc, detail)'):
    if needle not in fail_src:
        fail(f'provider timeout log hygiene missing: {needle}')
# Timeout branch must not pass the exception object to write_error_log.
timeout_block = fail_src[fail_src.find('if is_timeout:'):fail_src.find('else:', fail_src.find('if is_timeout:'))]
if 'write_error_log(' not in timeout_block or ', exc' in timeout_block:
    fail('expected timeout branch still forwards exception object/traceback')

print('LYRIC PIPELINE V29 TRANSPORT GENERATION + BURST ADMISSION REPLAY: PASS')
print('  hidden same-title end continuation requires playing + end dwell + no real rail: PASS')
print('  transport generation publishes the existing visual discontinuity serial without provider/identity restart: PASS')
print('  KuGou player-scoped zero-touch delay + atomic cross-restart lyric cache: PASS')
print('  burst admission retires only fading exits before placement: PASS')
print('  V28 precision visual handoff + atlas raster/packing semantics remain locked; H8 metadata wrapper relocation allowed: PASS')
print('  atlas stale-drop/capacity reserve/stage telemetry: PASS')
print('  expected provider timeout traceback suppression: PASS')
