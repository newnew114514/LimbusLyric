#!/usr/bin/env python3
import ast, pathlib, sys

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_PLAYER_PRESENCE_FETCH_GUARD_REPLAY.py <main.py>')
path = pathlib.Path(sys.argv[1])
source = path.read_text(encoding='utf-8')
tree = ast.parse(source)

def fn(name, class_name=None):
    if class_name:
        for c in tree.body:
            if isinstance(c, ast.ClassDef) and c.name == class_name:
                for n in c.body:
                    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name:
                        return n
        raise AssertionError(f'missing function {class_name}.{name}')
    hits=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name]
    if not hits: raise AssertionError(f'missing function {name}')
    return hits[0]

def text(name, class_name=None):
    n=fn(name, class_name)
    return '\n'.join(source.splitlines()[n.lineno-1:n.end_lineno])

def check(label, cond):
    if not cond: raise AssertionError(label)
    print(f'  {label}: PASS')

start=text('start','MediaSessionSync')
check('same active player start preserves confirmed liveness epoch',
      '_liveness_sync_was_requested' in start and 'old_stem != new_stem' in start and
      '_reset_player_liveness_epoch(new_stem)' in start and '_player_liveness_wake_event.set()' in start)

poll=text('_poll_loop','MediaSessionSync')
check('NetEase native log requires positive player liveness',
      "NETEASE_NATIVE_LOG_ENABLED and liveness_alive is True" in poll)
check('NetEase bridge fast-primary requires positive player liveness',
      "proc_hint_pre == 'cloudmusic' and liveness_alive is True" in poll and 'bridge_transport_fast' in poll)

monitor=text('_monitor_track_change','ControlPanel')
check('zero-touch first attach cannot consume metadata before positive liveness',
      "_player_liveness != 'alive'" in monitor and '_zero_touch_first_attach_pending' in monitor and
      monitor.index("_player_liveness != 'alive'") < monitor.index('_detected_player_track()'))
check('dead-player reopen path also waits for positive liveness', '_player_dead_waiting_reopen' in monitor)

detect=text('_detected_player_track','ControlPanel')
check('paused NetEase native-log identity is not accepted directly',
      '_stale_native_paused_identity' in detect and "position_source == 'ncm-native-log'" in detect and
      "media_status != 'playing'" in detect and 'not _stale_native_paused_identity' in detect)

manual=text('fetch_and_set','LyricFetcher')
check('manual fetch waits for bounded liveness proof',
      'PLAYER_LIVENESS_MANUAL_WAIT_MS' in manual and 'player_presence_ok' in manual and
      "live == 'alive'" in manual and "live == 'dead'" in manual)
check('manual fetch blocks stale automatic identity when player is absent',
      '手动抓词播放器未运行保护' in manual and 'auto-identity=blocked' in manual and 'stale-cache=blocked' in manual)
check('manual fetch rejects paused NetEase native-log identity',
      'stale_native_paused' in manual and "position_source == 'ncm-native-log'" in manual and
      "media_status != 'playing'" in manual)
check('window-title fallback requires confirmed player presence', 'if not song and player_presence_ok:' in manual)
check('offline manual lyric never binds a dead player clock',
      'if player_presence_ok:' in manual and '离线手动歌词不绑定播放器时钟' in manual)
check('offline manual lyric cannot hot-launch ghost overlay',
      "getattr(panel, '_is_started', False) and player_presence_ok" in manual)
check('QQ manual duration evidence is disabled without player presence',
      "if source == 'QQ音乐' and player_presence_ok:" in manual)

check('H10F1 build tag present', 'PLAYER-PRESENCE FETCH-GUARD H10F1' in source)
print('PLAYER PRESENCE FETCH GUARD REPLAY: PASS')
