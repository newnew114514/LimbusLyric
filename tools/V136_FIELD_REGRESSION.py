from __future__ import annotations

import ast
import pathlib
import sys

if len(sys.argv) != 2:
    raise SystemExit('usage: V136_FIELD_REGRESSION.py <main.py>')

path = pathlib.Path(sys.argv[1]).resolve()
src = path.read_text(encoding='utf-8')
tree = ast.parse(src)


def need(cond, msg):
    if not cond:
        print('V136 FIELD REGRESSION: FAIL')
        print(' - ' + msg)
        raise SystemExit(1)


for token in (
    'v1.8.9.136 RELEASE V136 FIELD REGRESSION CLOSURE',
    'V135 TRANSLATION OWNERSHIP HOTFIX',
    'V136模式切换身份竞态拒绝',
    'V136重新载入双语缓存重挂',
    '+ QQ MODERN SEARCH + COVER DIRECT-ID R9.2',
):
    need(token in src, 'missing marker: ' + token)

funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
for name in (
    '_v136_loaded_identity',
    '_v136_mode_refetch_identity_conflict',
    '_v136_refetch_loaded_track_for_mode_switch',
    '_v136_rehydrate_bilingual',
    '_v136_launch_current_lyrics',
    '_v136_activate_field_regression_closure',
):
    need(name in funcs, 'missing function: ' + name)

start = src.index('# V136 FIELD REGRESSION CLOSURE')
end = src.index('_v136_activate_field_regression_closure()', start) + len('_v136_activate_field_regression_closure()')
block = src[start:end]
for forbidden in (
    'sync_offset_ms =',
    'media_sync.start(',
    'MediaSessionSync.position =',
    'MediaSessionSync.seek =',
    'LyricSearchEngine.search =',
    'setChecked(',
):
    need(forbidden not in block, 'V136 layer crossed protected authority: ' + forbidden)

selected = [funcs[n] for n in (
    '_v136_loaded_identity',
    '_v136_mode_refetch_identity_conflict',
    '_v136_refetch_loaded_track_for_mode_switch',
    '_v136_rehydrate_bilingual',
    '_v136_launch_current_lyrics',
)]

logs = []
class ImmediateTimer:
    @staticmethod
    def singleShot(_ms, fn):
        fn()

class Status:
    def __init__(self): self.text = ''
    def setText(self, text): self.text = str(text)

class Toggle:
    def __init__(self, checked=True): self.checked = checked
    def isChecked(self): return self.checked

class Sync:
    def __init__(self, key=''): self._track_key = key

class Window:
    def __init__(self): self._h95f5_translation_lrc = ''

class Panel:
    def __init__(self, loaded='old|artist', media='old|artist', detected=('Old','Artist')):
        self._loaded_song = 'Old'
        self._loaded_artist = 'Artist'
        self._loaded_track_key = loaded
        self.media_sync = Sync(media)
        self.detected = detected
        self.status = Status()
        self._h95f5_bilingual_mode = 'bilingual'
        self._h95f5_translation_cache = {'old|artist': {'lyric': '[00:01.00]translation', 'source': '网易云'}}
        self.lyric_window = Window()
        self._is_started = True
        self.trans_check = Toggle(True)
        self.pre_calls = 0
        self.launch_calls = 0
    def _track_identity(self, song, artist):
        return (str(song).strip().lower() + '|' + str(artist).strip().lower()) if song else ''
    def _same_track(self, a, b, c, d):
        return self._track_identity(a,b) == self._track_identity(c,d)
    def _detected_player_track(self):
        return self.detected


def old_refetch(panel, **kwargs):
    panel.pre_calls += 1
    return 'old-refetch'

def old_launch(panel, *args, **kwargs):
    panel.launch_calls += 1
    panel.lyric_window._h95f5_translation_lrc = ''
    return True

def norm_mode(value): return str(value)
def panel_identity(panel): return panel._track_identity(panel._loaded_song, panel._loaded_artist), panel._loaded_song, panel._loaded_artist
def apply_cache(panel):
    identity, _, _ = panel_identity(panel)
    row = panel._h95f5_translation_cache.get(identity)
    if not row: return None
    panel.lyric_window._h95f5_translation_lrc = row['lyric']
    return True

ns = {
    'QTimer': ImmediateTimer,
    'write_error_log': lambda *a, **k: logs.append((a,k)),
    '_V136_MODE_REFETCH_PRE': old_refetch,
    '_V136_LAUNCH_PRE': old_launch,
    '_h95f5_norm_mode': norm_mode,
    '_h95f5_panel_identity_key': panel_identity,
    '_h95f5_apply_cached_translation': apply_cache,
}
exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), ns)

p = Panel(media='new|artist', detected=('New','Artist'))
result = ns['_v136_refetch_loaded_track_for_mode_switch'](p, reason='translation-toggle')
need(result is False, 'mixed identity mode-refetch was not vetoed')
need(p.pre_calls == 0, 'mixed identity still reached historical provider refetch')
need(p.trans_check.isChecked(), 'identity veto mutated the user translation preference')
need('等待当前歌曲身份稳定' in p.status.text, 'identity veto did not leave a clear wait state')

p2 = Panel(media='old|artist', detected=('Old','Artist'))
result2 = ns['_v136_refetch_loaded_track_for_mode_switch'](p2, reason='translation-toggle')
need(result2 == 'old-refetch' and p2.pre_calls == 1, 'same-track mode-refetch was incorrectly blocked')

p3 = Panel(media='', detected=('New','Artist'))
result3 = ns['_v136_refetch_loaded_track_for_mode_switch'](p3, reason='translation-toggle')
need(result3 is False and p3.pre_calls == 0, 'detected new identity did not veto stale refetch')

p4 = Panel()
p4.lyric_window._h95f5_translation_lrc = '[00:01.00]already-visible'
out4 = ns['_v136_launch_current_lyrics'](p4, start_delay=0)
need(out4 is True and p4.launch_calls == 1, 'historical launch did not execute exactly once')
need(p4.lyric_window._h95f5_translation_lrc == '[00:01.00]translation', 'cached bilingual sidecar was not reattached after relaunch')

p5 = Panel(); p5._h95f5_bilingual_mode = 'original'
out5 = ns['_v136_launch_current_lyrics'](p5)
need(out5 is True and p5.lyric_window._h95f5_translation_lrc == '', 'original-only relaunch incorrectly injected translation')

print('V136 FIELD REGRESSION: PASS')
print(' - mixed old-song/new-player mode-refetch is vetoed before provider search')
print(' - same-track mode-refetch remains on the historical path')
print(' - cached bilingual sidecar is reattached after relaunch/restart')
print(' - original-only mode and clock/seek/render authorities remain untouched')
