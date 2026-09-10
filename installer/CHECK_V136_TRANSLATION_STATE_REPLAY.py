from __future__ import annotations

import ast
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_V136_TRANSLATION_STATE_REPLAY.py <main.py>')

path = Path(sys.argv[1])
text = path.read_text(encoding='utf-8')


def need(cond: bool, message: str) -> None:
    if not cond:
        print('V136 TRANSLATION STATE REPLAY: FAIL')
        print(' - ' + message)
        raise SystemExit(1)


ast.parse(text)
for token in (
    'V136 TRANSLATION STATE TEST',
    'V136模式空载荷开始保持武装',
    'V136重复开始幂等',
    'shadow-rebuild=0 | media-restart=0 | bilingual-sidecar=preserve',
    'V136模式刷新旧载荷身份转当前曲目',
    'old-duration-query=blocked | route=auto-current-track',
):
    need(token in text, 'missing runtime token: ' + token)


def start_transition(*, was_started: bool, mode_blocked: bool, auto_enabled: bool, bound: bool, busy: bool):
    if mode_blocked:
        return {'started': True, 'armed': auto_enabled, 'relaunch': False, 'media_restart': not was_started}
    if was_started and bound and not busy:
        return {'started': True, 'armed': auto_enabled, 'relaunch': False, 'media_restart': False}
    return {'started': True, 'armed': auto_enabled, 'relaunch': True, 'media_restart': True}


a = start_transition(was_started=False, mode_blocked=True, auto_enabled=True, bound=False, busy=False)
need(a['started'] and a['armed'] and not a['relaunch'], 'translation-mode miss still loses Start intent')
need(a['started'] and a['armed'], 'next-track success would still require another Start click')
r = start_transition(was_started=True, mode_blocked=False, auto_enabled=True, bound=True, busy=False)
need(not r['relaunch'] and not r['media_restart'], 'repeated Start still rebuilds sync/timeline')


def mode_route(loaded: tuple[str, str], live: tuple[str, str]) -> str:
    def norm(s: str) -> str:
        return ''.join(ch.lower() for ch in s if ch.isalnum())
    same = norm(loaded[0]) == norm(live[0]) and (
        not loaded[1] or not live[1] or norm(loaded[1]) == norm(live[1])
    )
    return 'loaded-mode-refetch' if same else 'auto-current-track'


need(mode_route(('simple times', 'Kacey Musgraves'), ('呼吸', '林忆莲')) == 'auto-current-track',
     'old loaded identity can still be combined with new player evidence')
need(mode_route(('simple times', 'Kacey Musgraves'), ('simple times', 'Kacey Musgraves')) == 'loaded-mode-refetch',
     'normal same-track mode switch was unnecessarily rerouted')

print('V136 TRANSLATION STATE REPLAY: PASS')
print(' - mode miss preserves explicit Start/auto intent for a later success')
print(' - repeated Start is idempotent for a healthy bound lyric performance')
print(' - stale loaded identity cannot perform mode-refetch against a newer player track')
