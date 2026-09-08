from __future__ import annotations
import ast, os, re, sys, textwrap, threading, time, urllib.parse
from pathlib import Path


def collect(text: str):
    tree = ast.parse(text)
    lines = text.splitlines()
    out = {}
    def walk(body, prefix=''):
        for node in body:
            if isinstance(node, ast.ClassDef):
                walk(node.body, f'{prefix}.{node.name}' if prefix else node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = f'{prefix}.{node.name}' if prefix else node.name
                out[q] = '\n'.join(lines[node.lineno-1:node.end_lineno]) + '\n'
    walk(tree.body)
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: CHECK_QQ_LATEST_LOG_REPLAY.py <main.py>')
        return 2
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    funcs = collect(source)
    need = {
        'AsyncPlayerUiPositionReader.set_qq_gesture_candidate_quarantine',
        'AsyncPlayerUiPositionReader.poll',
        'LyricSearchEngine.search_qq',
        'ControlPanel._request_auto_track',
        'ControlPanel._start_auto_search_job',
        'LyricFetcher.get_qq_ui_duration_hint',
        'LyricFetcher.fetch_and_set',
        'ControlPanel._monitor_track_change',
        'ControlPanel._restore_qq_suspended_loaded_track',
        'ControlPanel._on_qq_auto_lyric_transaction_result',
        'ControlPanel._refetch_loaded_track_for_mode_switch',
    }
    missing = sorted(need - funcs.keys())
    if missing:
        print('QQ LATEST-LOG REPLAY: FAIL')
        for q in missing:
            print('  - missing ' + q)
        return 61

    # Reproduce the 10:40:34 bug shape: stale-control reacquire returned a first,
    # unvalidated 92s candidate during a physical rail gesture. It must be hidden from
    # generic merge until the QQ adapter publishes the validated second sample.
    set_code = textwrap.dedent(funcs['AsyncPlayerUiPositionReader.set_qq_gesture_candidate_quarantine']).replace(
        'def set_qq_gesture_candidate_quarantine', 'def replay_set_quarantine', 1)
    poll_code = textwrap.dedent(funcs['AsyncPlayerUiPositionReader.poll']).replace(
        'def poll', 'def replay_poll', 1)
    g = {'os': os, 'time': time}
    exec(set_code, g)
    exec(poll_code, g)
    setq = g['replay_set_quarantine']; poll = g['replay_poll']

    class Alive:
        def is_alive(self): return True
    class DummyAsync:
        def __init__(self):
            self._lock = threading.Lock()
            self._process_name = 'qqmusic.exe'
            self._thread = Alive()
            self._suspended = False
            self._expected_duration_ms = 185000
            self._cached = {
                'position_ms': 92000, 'duration_ms': 185000, 'confidence': 128,
                'source': 'qq-time-pair-candidate', 'source_key': 'pair', '_sample_seq': 10,
            }
        def start(self, process_name): raise AssertionError('unexpected start')
        def _is_cloudmusic_process(self, process_name): return False
        def _guard_qq_duration_mismatch_result(self, reader, process_name, result): return result
    d = DummyAsync()
    if not setq(d, 11.2):
        print('QQ LATEST-LOG REPLAY: FAIL\n  - could not arm candidate quarantine')
        return 62
    held = poll(d, 'qqmusic.exe')
    if held.get('position_ms') is not None or held.get('source') != 'qq-gesture-candidate-quarantine':
        print('QQ LATEST-LOG REPLAY: FAIL\n  - 92s unvalidated reacquire candidate escaped quarantine')
        return 63
    d._cached = {
        'position_ms': 92000, 'duration_ms': 185000, 'confidence': 168,
        'source': 'qq-time-pair-validated', 'source_key': 'pair', '_sample_seq': 11,
    }
    validated = poll(d, 'qqmusic.exe')
    if validated.get('position_ms') != 92000 or validated.get('source') != 'qq-time-pair-validated':
        print('QQ LATEST-LOG REPLAY: FAIL\n  - validated sample was incorrectly quarantined')
        return 64

    # Exercise the actual search_qq selection code with a mocked QQ response containing
    # two same-title/same-artist versions: the historical bad 148s row first and the
    # player's real 264s row second. Expected duration must choose the 264s version.
    search_code = textwrap.dedent(funcs['LyricSearchEngine.search_qq']).replace(
        'def search_qq', 'def replay_search_qq', 1)
    logs = []
    class Resp:
        def __init__(self, payload): self.payload = payload
        def raise_for_status(self): return None
        def json(self): return self.payload
    class Requests:
        def get(self, url, *args, **kwargs):
            if 'client_search_cp' in url:
                return Resp({'data': {'song': {'list': [
                    {'songname':'IF YOU','singer':[{'name':'BIGBANG'}], 'interval':148, 'songmid':'wrong148', 'songid':1},
                    {'songname':'IF YOU','singer':[{'name':'BIGBANG (빅뱅)'}], 'interval':264, 'songmid':'right264', 'songid':2},
                ]}}})
            if 'fcg_query_lyric_new' in url:
                lyric = '[00:00.00]RIGHT-264' if 'right264' in url else '[00:00.00]WRONG-148'
                return Resp({'code':0, 'lyric':lyric, 'trans':''})
            return Resp({'data': []})
        def post(self, *args, **kwargs): return Resp({})
    requests = Requests()

    def clean(v): return re.sub(r'[^0-9a-z\u4e00-\u9fff\uac00-\ud7af]+','',str(v or '').lower())
    def artist_text(obj):
        return '/'.join(str(x.get('name') or '') for x in (obj.get('singer') or []))
    def artist_match(q,c):
        qk=clean(q); ck=clean(c)
        # BIGBANG (빅뱅) vs BIGBANG is a valid conservative containment alias for this replay.
        return (bool(qk and ck and (qk==ck or qk in ck or ck in qk)), qk if qk else '')
    def score(qs,qa,cs,ca):
        s=100 if clean(qs)==clean(cs) else 0
        ok,_=artist_match(qa,ca)
        return s+(62 if ok else 0)
    class FakeEngine:
        HEADERS={}
        last_error=''
        @staticmethod
        def _best(items, song, artist, ng, ag): return max(items, key=lambda x: score(song,artist,ng(x),ag(x))) if items else None
        @staticmethod
        def _fail(provider, exc=None, detail=''):
            FakeEngine.last_error=f'{provider}: {detail}'
            return None,None,0
        @staticmethod
        def _decode_qq_lyric(v): return str(v or '')
        @staticmethod
        def _decode_qq_translation(v, allow_plain=False): return str(v or '')
    g2 = {
        'requests': requests, 'urllib': urllib, 're': re, 'html': __import__('html'),
        'concurrent': __import__('concurrent'), 'time': time,
        'LyricSearchEngine': FakeEngine, '_clean_name': clean, '_artist_text': artist_text,
        '_artist_alias_match': artist_match, '_candidate_score': score,
        'write_error_log': lambda *a, **k: logs.append((a,k)),
        'WORD_TIMING_ENABLED': False, 'WORD_CLOCK_RECOVERY_ENABLED': False,
        'QQ_NATIVE_QRC_ENABLED': True, 'CROSS_SOURCE_TIMING_ENABLED': False,
        'QQ_CROSS_SOURCE_TIMING_ENABLED': False,
    }
    exec(search_code, g2)
    search = g2['replay_search_qq']
    lyric, _trans, duration = search('IF YOU', 'BIGBANG (빅뱅)', False, 264000)
    if duration != 264000 or 'RIGHT-264' not in str(lyric or ''):
        print('QQ LATEST-LOG REPLAY: FAIL')
        print(f'  - duration identity did not choose 264s IF YOU: duration={duration} lyric={lyric!r}')
        return 65

    # When only the 148s wrong version is available, strict expected-duration search must
    # fail closed rather than install Chinese/other same-title lyrics.
    class RequestsWrongOnly(Requests):
        def get(self, url, *args, **kwargs):
            if 'client_search_cp' in url:
                return Resp({'data': {'song': {'list': [
                    {'songname':'IF YOU','singer':[{'name':'BIGBANG'}], 'interval':148, 'songmid':'wrong148', 'songid':1},
                ]}}})
            return super().get(url, *args, **kwargs)
    g3 = dict(g2); g3['requests'] = RequestsWrongOnly(); g3['LyricSearchEngine'] = FakeEngine
    exec(search_code, g3)
    bad_lyric, _bad_trans, bad_duration = g3['replay_search_qq']('IF YOU','BIGBANG (빅뱅)',False,264000)
    if bad_lyric is not None or bad_duration != 0:
        print('QQ LATEST-LOG REPLAY: FAIL\n  - wrong 148s same-title version did not fail closed')
        return 66

    # Static wiring checks: auto-track must capture QQ UIA duration and result/cache must
    # preserve duration identity through the background search.
    req = funcs['ControlPanel._request_auto_track']
    worker = funcs['ControlPanel._start_auto_search_job']
    for token in ('QQ自动歌词搜索时长证据', "self.media_sync._uia_reader.poll('qqmusic.exe')", "'provider_duration_ms': provider_duration_ms"):
        if token not in req:
            print('QQ LATEST-LOG REPLAY: FAIL\n  - auto-track duration wiring missing: '+token)
            return 67
    for token in ('duration_cache_key', 'QQ自动歌词版本时长拒绝', 'identity_duration_ms'):
        if token not in worker:
            print('QQ LATEST-LOG REPLAY: FAIL\n  - auto-result duration defense missing: '+token)
            return 68

    # 11:02 latest-log regression: manual first fetch already had a reliable 04:24 QQ
    # duration, so the manual path must forward that evidence into provider selection and
    # keep an independent final mismatch guard. The strict QQ search must also look deeper
    # than the historical top eight candidates.
    manual = funcs['LyricFetcher.fetch_and_set']
    qqsearch = funcs['LyricSearchEngine.search_qq']
    mode_refetch = funcs['ControlPanel._refetch_loaded_track_for_mode_switch']
    for token in (
        "get_qq_ui_duration_hint(panel, 'manual-fetch')",
        'provider_duration_ms=provider_duration_ms',
        'QQ手动歌词版本时长拒绝',
    ):
        if token not in manual:
            print('QQ LATEST-LOG REPLAY: FAIL\n  - manual first-fetch duration defense missing: '+token)
            return 69
    for token in ('search_limit = 30 if expected_duration_ms > 0 else 8', 'n={search_limit}'):
        if token not in qqsearch:
            print('QQ LATEST-LOG REPLAY: FAIL\n  - strict QQ search-depth defense missing: '+token)
            return 70
    if "get_qq_ui_duration_hint(self, 'mode-refetch')" not in mode_refetch or 'provider_duration_ms=provider_duration_ms' not in mode_refetch:
        print('QQ LATEST-LOG REPLAY: FAIL\n  - QQ mode-refetch duration identity wiring missing')
        return 71

    # Exercise the actual duration-evidence helper using the 11:02:24 shape.
    hint_code = textwrap.dedent(funcs['LyricFetcher.get_qq_ui_duration_hint']).replace(
        'def get_qq_ui_duration_hint', 'def replay_duration_hint', 1)
    hlogs=[]
    gh={'write_error_log':lambda *a,**k:hlogs.append((a,k))}
    exec(hint_code, gh)
    class HintReader:
        def poll(self, proc):
            return {'duration_ms':264000, 'source':'qq-time-pair-candidate', 'position_ms':171000}
    class HintSync: _uia_reader=HintReader()
    class HintPanel: media_sync=HintSync()
    if gh['replay_duration_hint'](HintPanel(), 'manual-fetch') != 264000:
        print('QQ LATEST-LOG REPLAY: FAIL\n  - manual 04:24 QQ duration evidence was not captured')
        return 72

    # 11:03:16 failure transaction: no safe IF YOU lyrics must unlock _auto_target_key
    # while preserving the fact that the previous loaded overlay is suspended.
    txn_code = textwrap.dedent(funcs['ControlPanel._on_qq_auto_lyric_transaction_result']).replace(
        'def _on_qq_auto_lyric_transaction_result', 'def replay_txn_result', 1)
    gt={'time':time, 'write_error_log':lambda *a,**k:None}
    exec(txn_code, gt)
    class Check: 
        def isChecked(self): return False
    class AutoCheck:
        def isChecked(self): return True
    class Txn:
        _is_started=True; _auto_armed=True; auto_track_check=AutoCheck(); trans_check=Check()
        _auto_generation=7; _auto_target_key='ifyou|bigbang'; _auto_overlay_suspended=True
        _auto_candidate_key='x'; _auto_candidate_hits=2
    t=Txn()
    gt['replay_txn_result'](t, {
        'source':'QQ音乐','generation':7,'key':'ifyou|bigbang','song':'IF YOU',
        'artist':'BIGBANG (빅뱅)','trans_only':False,'lyric':None,
    })
    if getattr(t,'_auto_target_key',None) != '' or getattr(t,'_auto_failed_track_key','') != 'ifyou|bigbang' or not getattr(t,'_auto_overlay_suspended',False):
        print('QQ LATEST-LOG REPLAY: FAIL\n  - failed IF YOU provisional transaction did not unlock cleanly')
        return 73

    # Returning to the previous successfully loaded track must rebind and relaunch its
    # still-cached lyrics instead of being swallowed by the same-track fast path.
    restore_code = textwrap.dedent(funcs['ControlPanel._restore_qq_suspended_loaded_track']).replace(
        'def _restore_qq_suspended_loaded_track', 'def replay_restore_loaded', 1)
    gr={'write_error_log':lambda *a,**k:None}
    exec(restore_code, gr)
    class TextBox:
        def toPlainText(self): return '[00:00.00]cached old lyric'
    class LyricWin: song_duration=219000
    class Combo:
        def currentText(self): return 'QQ音乐'
    class Status:
        def setText(self, v): self.value=v
    class Sync:
        def __init__(self): self.bound=None
        def bind_track(self,*args,**kwargs): self.bound=(args,kwargs)
    class Restore:
        _auto_overlay_suspended=True; _loaded_source='QQ音乐'; _loaded_song='我活着'; _loaded_artist='福梦 (FUMON)'
        _auto_target_key=''; _auto_failed_track_key='ifyou|bigbang'; _auto_failed_until=time.monotonic()+20
        _auto_candidate_key=''; _auto_candidate_hits=0; _auto_suspended_loaded_key='我活着|福梦fumon'
        player_combo=Combo(); text_input=TextBox(); lyric_window=LyricWin(); status=Status()
        def __init__(self): self.media_sync=Sync(); self.launched=False
        def _same_track(self,a,b,c,d): return a==c
        def _launch_current_lyrics(self,start_delay=0): self.launched=True
    r=Restore()
    if not gr['replay_restore_loaded'](r,'我活着','福梦 (FUMON)') or not r.launched or not r.media_sync.bound:
        print('QQ LATEST-LOG REPLAY: FAIL\n  - return-to-old-track cached lyrics were not restored')
        return 74

    # The monitor must actually call that restore before its historical same-track early return.
    monitor_code = textwrap.dedent(funcs['ControlPanel._monitor_track_change']).replace(
        'def _monitor_track_change', 'def replay_monitor', 1)
    gm={'time':time, 'write_error_log':lambda *a,**k:None}
    exec(monitor_code, gm)
    class MonitorSync:
        def snapshot(self): return {'player_liveness':'unknown'}
    class Mon:
        _is_started=True; _auto_armed=True; auto_track_check=AutoCheck(); _loaded_song='我活着'; _loaded_artist='福梦'
        media_sync=MonitorSync()
        _auto_candidate_key=''; _auto_candidate_hits=0; _auto_target_key=''; _auto_failed_track_key=''; _auto_failed_until=0
        _auto_transport_hint_source='x'
        def __init__(self, detected): self.detected=detected; self.restored=False; self.requested=[]
        def _detected_player_track(self): return self.detected
        def _same_track(self,a,b,c,d): return a==c
        def _restore_qq_suspended_loaded_track(self,a,b): self.restored=True; return True
        def _restore_reopened_player_if_cached(self,state,a,b): return False
        def _handle_selected_player_dead(self,state): return False
        def _track_identity(self,a,b): return a+'|'+b
        def _active_auto_target_matches(self,a,b): return False
        def _auto_transport_hint_active(self): return True
        def _request_auto_track(self,a,b): self.requested.append((a,b))
    m=Mon(('我活着','福梦'))
    gm['replay_monitor'](m)
    if not m.restored:
        print('QQ LATEST-LOG REPLAY: FAIL\n  - same-loaded monitor path still swallowed suspended overlay restore')
        return 75

    # A different track after the failed target must still be requestable immediately.
    m2=Mon(('雨爱','杨丞琳')); m2._loaded_song='我活着'; m2._auto_failed_track_key='ifyou|bigbang'; m2._auto_failed_until=time.monotonic()+20
    m2._restore_qq_suspended_loaded_track=lambda a,b: False
    gm['replay_monitor'](m2)
    if not m2.requested or m2.requested[-1][0] != '雨爱':
        print('QQ LATEST-LOG REPLAY: FAIL\n  - different track remained blocked after failed IF YOU target')
        return 76

    print('QQ LATEST-LOG REPLAY: PASS')
    print('  stale-reacquire 92s candidate held until validation: PASS')
    print('  validated QQ sample still reaches existing gesture FSM: PASS')
    print('  IF YOU 264s version beats wrong 148s same-title row: PASS')
    print('  wrong-only 148s result fails closed: PASS')
    print('  auto-track/cache/result duration identity wiring: PASS')
    print('  manual/mode QQ duration identity + strict deeper search: PASS')
    print('  failed provisional target unlock + return-to-old-track restore: PASS')
    print('  different track remains detectable after failed target: PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
