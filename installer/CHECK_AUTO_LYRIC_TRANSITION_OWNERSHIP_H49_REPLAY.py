from pathlib import Path
import ast
import sys
import time

if len(sys.argv) not in (2, 3):
    raise SystemExit(2)

source = Path(sys.argv[1])
text = source.read_text(encoding='utf-8')


def need(condition, message):
    if not condition:
        print('AUTO LYRIC TRANSITION OWNERSHIP H49 REPLAY: FAIL')
        print(' - ' + message)
        raise SystemExit(1)


if len(sys.argv) == 3:
    field = Path(sys.argv[2]).read_text(encoding='utf-8', errors='replace')
    need('H44网易云过期异步歌词结果拒绝' in field,
         'field fixture does not contain the H44 async-result veto')
    need('手动抓词已合并当前自动任务' in field,
         'field fixture does not contain the stuck in-flight/manual coalesce symptom')

for marker in (
    '+ AUTO LYRIC TRANSITION OWNERSHIP H49',
    'H49网易云旧Native身份不得误杀当前自动歌词',
    'H49网易云身份冲突释放自动歌词事务',
    'H49_NETEASE_NATIVE_TRANSITION_GRACE_MS',
):
    need(marker in text, 'missing H49 marker: ' + marker)

tree = ast.parse(text)
helper = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_h49_ncm_auto_result_policy'), None)
need(helper is not None, 'H49 policy helper is missing')
h41 = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_h41_auto_result'), None)
need(h41 is not None, 'H41 auto-result wrapper is missing')
h41_src = ast.get_source_segment(text, h41) or ''
need('_h49_ncm_auto_result_policy' in h41_src, 'H41 veto is not wired through H49 policy')
need("panel._auto_fetch_in_progress = False" in h41_src and "panel._auto_target_key = ''" in h41_src,
     'current rejected transaction is not explicitly released')
need("if bool(h49.get('current'))" in h41_src,
     'stale/non-current results could incorrectly release a newer transaction')

assign = next(
    n for n in tree.body
    if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == 'H49_NETEASE_NATIVE_TRANSITION_GRACE_MS' for t in n.targets)
)

class Combo:
    def __init__(self, value): self.value = value
    def currentText(self): return self.value

class Toggle:
    def __init__(self, value): self.value = bool(value)
    def isChecked(self): return self.value

class Sync:
    pass

class Panel:
    def __init__(self, now):
        self.player_combo = Combo('网易云音乐')
        self.source_combo = Combo('网易云')
        self.auto_track_check = Toggle(True)
        self.trans_check = Toggle(False)
        self._is_started = True
        self._auto_armed = True
        self._auto_generation = 7
        self._auto_target_key = 'newsong|newartist'
        self._loaded_song = 'Old Song'
        self._loaded_artist = 'Old Artist'
        self.media_sync = Sync()
        self.media_sync._track_key = 'newsong|newartist'
        self.media_sync._netease_native_transition_started_mono = now - 900.0
        self.media_sync._track_bound_mono = now - 250.0
    @staticmethod
    def _same_track(a, b, c, d):
        clean = lambda s: ''.join(ch.lower() for ch in str(s or '') if ch.isalnum())
        return bool(clean(a) and clean(a) == clean(c) and (not clean(b) or not clean(d) or clean(b) == clean(d)))

runtime = {'time': time}
exec(compile(ast.Module(body=[assign, helper], type_ignores=[]), str(source), 'exec'), runtime)
policy = runtime['_h49_ncm_auto_result_policy']
now = time.monotonic() * 1000.0
row = {
    'generation': 7, 'key': 'newsong|newartist', 'source': '网易云',
    'trans_only': False, 'lyric': '[00:01.00]new', 'song': 'New Song', 'artist': 'New Artist',
}

# Exact field-race shape: provisional bind owns new song while native still reports loaded old song.
p = Panel(now)
d = policy(p, row, 'Old Song', 'Old Artist', now_ms=now)
need(d.get('current') is True and d.get('allow') is True,
     'recent real track edge still lets old native identity kill the current new-song result')

# A parsing wobble without a fresh native edge must remain fail-closed.
p2 = Panel(now)
p2.media_sync._netease_native_transition_started_mono = now - 20000.0
d = policy(p2, row, 'Old Song', 'Old Artist', now_ms=now)
need(d.get('current') is True and d.get('allow') is False and d.get('reason') == 'no-recent-native-track-edge',
     'old transition evidence can authorize an unrelated/misparsed result')

# If native has already moved away from the loaded old payload, it is authoritative against this result.
p3 = Panel(now)
d = policy(p3, row, 'Another Song', 'Another Artist', now_ms=now)
need(d.get('current') is True and d.get('allow') is False,
     'new native identity is incorrectly treated as lagging old identity')

# An obsolete generation is never allowed to affect current in-flight bookkeeping.
p4 = Panel(now)
old = dict(row); old['generation'] = 6
d = policy(p4, old, 'Old Song', 'Old Artist', now_ms=now)
need(d.get('current') is False and d.get('allow') is False,
     'obsolete generation gained H49 transition ownership')

# A result not bound by MediaSync cannot use only the UI transaction key as identity proof.
p5 = Panel(now); p5.media_sync._track_key = 'different|track'
d = policy(p5, row, 'Old Song', 'Old Artist', now_ms=now)
need(d.get('current') is True and d.get('allow') is False and d.get('reason') == 'current-not-provisionally-bound',
     'unbound result gained display authority')

# Execute the real H41 wrapper with H49 present: the proven race must reach the historical
# display handler, while a current unproven mismatch must release its stuck transaction.
h38 = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_h38_ncm_current_identity')
runtime2 = {
    'time': time,
    'write_error_log': lambda *a, **k: None,
    '_h38_duration_conflict': lambda a, b: False,
    '_LIMBUS_H41_AUTO_RESULT_PRE': lambda panel, result: setattr(panel, 'base_rows', getattr(panel, 'base_rows', 0) + 1) or True,
}
exec(compile(ast.Module(body=[assign, helper, h38, h41], type_ignores=[]), str(source), 'exec'), runtime2)

p6 = Panel(now)
p6.media_sync._h38_ncm_player_duration_epoch = 0
p6.media_sync._media_player_epoch = 0
p6.media_sync._h38_ncm_player_duration_ms = 180000
p6.media_sync._h38_ncm_player_title = 'Old Song'
p6.media_sync._h38_ncm_player_artist = 'Old Artist'
p6._h38_version_reconcile_sig = ''
p6._h38_version_reconcile_mono = 0.0
p6._h38_loaded_candidate_duration_ms = 0
p6._h38_loaded_candidate_track = ''
p6._h38_loaded_candidate_source = ''
p6._h39_ncm_accepted_payload_key = ''
p6._h39_ncm_accepted_payload_duration_ms = 0
p6._h39_ncm_accepted_payload_mono = 0.0
p6._auto_fetch_in_progress = True
p6._auto_candidate_key = ''
p6._auto_candidate_hits = 0
runtime2['_h41_auto_result'](p6, dict(row))
need(getattr(p6, 'base_rows', 0) == 1, 'proven field-race result still did not reach display handler')

p7 = Panel(now)
p7.media_sync._h38_ncm_player_duration_epoch = 0
p7.media_sync._media_player_epoch = 0
p7.media_sync._h38_ncm_player_duration_ms = 180000
p7.media_sync._h38_ncm_player_title = 'Old Song'
p7.media_sync._h38_ncm_player_artist = 'Old Artist'
p7.media_sync._netease_native_transition_started_mono = now - 20000.0
p7._h38_version_reconcile_sig = ''
p7._h38_version_reconcile_mono = 0.0
p7._auto_fetch_in_progress = True
p7._auto_candidate_key = 'newsong|newartist'
p7._auto_candidate_hits = 2
runtime2['_h41_auto_result'](p7, dict(row))
need(getattr(p7, 'base_rows', 0) == 0, 'unproven mismatch reached display handler')
need(p7._auto_fetch_in_progress is False and p7._auto_target_key == '' and p7._auto_candidate_hits == 0,
     'unproven current mismatch still leaves the auto transaction stuck')

print('AUTO LYRIC TRANSITION OWNERSHIP H49 REPLAY: PASS')
print(' - current new-song result survives only the proven old-native publication lag window')
print(' - no-edge/misparsed and already-new-native mismatches remain rejected')
print(' - current rejected transactions are released without touching obsolete/newer jobs')
