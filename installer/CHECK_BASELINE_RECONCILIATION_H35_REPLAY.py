from pathlib import Path
import ast, os, sys, time

if len(sys.argv) != 2:
    raise SystemExit(2)
source_path = Path(sys.argv[1])
text = source_path.read_text(encoding='utf-8')

def need(cond, msg):
    if not cond:
        print('BASELINE RECONCILIATION H35 REPLAY: FAIL')
        print(' - ' + msg)
        raise SystemExit(1)

markers = [
    '+ BASELINE RECONCILIATION H35',
    'H35紧急渲染保留多字幕',
    'H35网易云Seek候选暂缓',
    'H35网易云Seek二次确认',
    'H35 QQ纯音乐时长三方闭环',
    'H35酷狗既有播放假零阻断',
    'H35同曲歌手分隔符兼容',
    'H35字幕容量变更追踪',
    "LyricWindow.paintEvent._limbus_emergency_capacity = 'history+fading-preserved'",
    "MediaSessionSync._poll_netease_native_clock._limbus_seek_policy = 'two-native-sample-proof'",
    "MediaSessionSync._kugou_seed_rail_local_master._limbus_existing_attach = 'synthetic-zero-bottom-guard'",
    "ControlPanel._on_auto_lyric_result._limbus_qq_instrumental_duration = 'two-uia-sample-rescue'",
]
for marker in markers:
    need(marker in text, 'missing H35 marker: ' + marker)
need("int(sys.getwindowsversion().build or 0) < 22000" in text, 'Win10 playback GC guard is not OS-scoped')
need("'manual-zero-bootstrap', 'auto-track-bootstrap', 'lazy-zero-bootstrap'" in text, 'KuGou synthetic-zero bottom guard is incomplete')
need('_h35_draw_plain_history_rows(window, event)' in text, 'emergency renderer does not preserve resident/fading rows')

# Extract only H35 constants/helpers/activation. This executes no GUI/application startup.
tree = ast.parse(text)
wanted_assign = {
    'H35_NCM_SEEK_JUMP_MS', 'H35_NCM_SEEK_SERIAL_MIN_DELTA_MS',
    'H35_NCM_SEEK_CONFIRM_MIN_MS', 'H35_NCM_SEEK_CONFIRM_TTL_MS',
    'H35_QQ_DURATION_CONFIRM_MIN_MS', 'H35_QQ_DURATION_CONFIRM_TTL_MS',
    'H35_KUGOU_SYNTHETIC_ZERO_REASONS',
}
wanted_funcs = {
    '_h35_ncm_seek_guard_step', '_h35_qq_duration_sample_step', '_h35_activate_runtime'
}
nodes = []
for node in tree.body:
    if isinstance(node, ast.Assign):
        names = {t.id for t in node.targets if isinstance(t, ast.Name)}
        if names & wanted_assign:
            nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in wanted_funcs:
        nodes.append(node)
ns = {'os': os, 'sys': sys, 'time': time}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source_path), 'exec'), ns)
need(wanted_assign <= set(ns), 'failed to extract H35 constants')

# NetEase: one bad frame is held and a reversion never publishes Seek.
step = ns['_h35_ncm_seek_guard_step']
a, p, out, ok, reason = step(None, None, 10000, 0, 'playing', 'song|artist', 1)
need(out == 10000 and not ok and reason == 'track-init', 'native initial anchor failed')
a0 = dict(a)
a, p, out, ok, reason = step(a, None, 50000, 1000, 'playing', 'song|artist', 2)
need(not ok and reason == 'hold-for-second-proof' and 10500 <= out <= 11500, 'one-frame native jump was not held')
a, p, out, ok, reason = step(a, p, 11100, 1100, 'playing', 'song|artist', 1)
need(not ok and reason == 'continuous' and out == 11100, 'false native jump did not recover without a Seek')

# A real same-track discontinuity is held once, then committed on coherent second evidence.
a = a0
p = None
a, p, out, ok, reason = step(a, p, 50000, 1000, 'playing', 'song|artist', 2)
need(not ok and p is not None, 'real discontinuity did not enter pending proof')
a, p, out, ok, reason = step(a, p, 50120, 1120, 'playing', 'song|artist', 2)
need(ok and reason == 'confirmed-discontinuity' and out == 50120, 'coherent second native sample did not confirm Seek')

# QQ instrumental: lyric duration never wins alone; two distinct matching QQ UIA samples are required.
qstep = ns['_h35_qq_duration_sample_step']
q, accepted = qstep(None, 10, 0, 146000, 'qq-time-pair-candidate', 0, 146000)
need(not accepted and int(q.get('hits', 0)) == 1, 'first QQ duration sample incorrectly became authority')
q, accepted = qstep(q, 11, 1000, 146000, 'qq-time-pair-candidate', 240, 146000)
need(accepted and int(q.get('hits', 0)) >= 2, 'two coherent QQ duration samples did not close first-attach proof')
q2, accepted2 = qstep(None, 1, 0, 150000, 'qq-time-pair-candidate', 0, 146000)
need(q2 is None and not accepted2, 'mismatched lyric/UIA duration was accepted')

# Minimal install smoke: H35 must wrap the fully installed runtime classes without startup.
class LW:
    def paintEvent(self, event): return 'paint'
    def set_max_visible_subtitles(self, value): self.max_visible_subtitles = value
class MS:
    def _kugou_seed_rail_local_master(self, *a, **k): return True
    def _poll_netease_native_clock(self, status_hint='unknown'): return None
    def _mark_seek_burst(self, *a, **k): return None
    def _process_stem(self, value): return str(value).lower().removesuffix('.exe')
class CP:
    def _warmup_selected_player(self): return None
    def _on_auto_lyric_result(self, row): return row
    def _complete_same_track_duration(self, *a, **k): return True
ns.update({
    'LyricWindow': LW, 'MediaSessionSync': MS, 'ControlPanel': CP,
    'write_error_log': lambda *a, **k: None,
    'PLAYBACK_GC_GUARD_ENABLED': False,
})
ns['_h35_activate_runtime'].__globals__.update(ns)
ns['_h35_activate_runtime']()
need(getattr(LW.paintEvent, '_limbus_layer', '') == 'H35', 'H35 renderer wrapper not installed')
need(getattr(MS._poll_netease_native_clock, '_limbus_layer', '') == 'H35', 'H35 NetEase wrapper not installed')
need(getattr(MS._kugou_seed_rail_local_master, '_limbus_layer', '') == 'H35', 'H35 KuGou seed wrapper not installed')
need(getattr(CP._on_auto_lyric_result, '_limbus_layer', '') == 'H35', 'H35 auto-result wrapper not installed')

# The base implementation downgrades synthetic zero after this wrapper runs.
# H35 must therefore ignore an eager caller's temporary absolute=True tag itself.
sync = MS()
sync._media_player_epoch = 2
sync._h35_kugou_existing_attach_block_epoch = 2
sync._h35_kugou_zero_block_log_mono = 0.0
sync._process_hint = 'kgmusic.exe'
need(sync._kugou_seed_rail_local_master(
    0, status='playing', reason='manual-zero-bootstrap', absolute=True, now_ms=5000
) is False, 'existing KuGou playback accepted an eager absolute synthetic zero')

print('BASELINE RECONCILIATION H35 REPLAY: PASS')
print(' - emergency rendering preserves logical multi-subtitle history/fading rows')
print(' - NetEase native discontinuities require two coherent samples; one-frame jumps are held')
print(' - QQ instrumental duration requires lyric candidate + two matching UIA samples')
print(' - KuGou existing-playback synthetic-zero block and same-track alias reconciliation are installed')
print(' - Win10 playback-scoped cyclic-GC guard is enabled without changing Win11 default')
