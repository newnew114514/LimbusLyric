from __future__ import annotations

import ast
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_OUTPUT_DIY_SPOTIFY_H13_REPLAY.py <main.py>')
path = Path(sys.argv[1])
text = path.read_text(encoding='utf-8')
tree = ast.parse(text)


def need(cond, msg):
    if not cond:
        raise AssertionError(msg)

need('OUTPUT DIY SPOTIFY H13' in text, 'build tag missing H13')
need("PLAYER_BUILTIN_ORDER = ('网易云音乐', 'QQ音乐', '酷狗音乐', 'Spotify')" in text,
     'Spotify missing from built-in player order')
need('"Spotify": {' in text and '"process": "spotify.exe"' in text,
     'Spotify default player profile missing')

start = text.index('# H13 output / lyric-slot / Spotify extensions')
h14 = text.index('# H14 auto-precision deadline / bounded enhancement')
main_guard = text.index('if __name__ == "__main__":')
need(start < h14 < main_guard, 'H13/H14 runtime extension ordering is invalid')
h13 = text[start:h14]

# H13 playback is intentionally local Windows GSMTC only. Later lyric-only layers may add
# network lyric fallbacks, so scope this transport/auth prohibition to the H13 block itself.
for forbidden in ('api.spotify.com', 'accounts.spotify.com', 'client_secret', 'refresh_token', 'Authorization: Bearer'):
    need(forbidden not in h13, f'forbidden Spotify Web API/auth dependency: {forbidden}')
need("return 'spotify' in str(source or '').replace('\\\\','/').lower()" in h13,
     'Spotify GSMTC source affinity missing')
need("if cls._process_stem(process_name)=='spotify': return True" in h13,
     'Spotify is not a strict process-affine builtin')
need("supported=('cloudmusic','qqmusic','kgmusic','spotify')" in h13,
     'Spotify missing from bounded player liveness worker')
need('CreateToolhelp32Snapshot.restype=_wt.HANDLE' in h13 and
     'Process32FirstW.argtypes=[_wt.HANDLE,ctypes.POINTER(_PE)]' in h13 and
     'CloseHandle.argtypes=[_wt.HANDLE]' in h13,
     'Spotify Toolhelp probe lacks 64-bit-safe Win32 ABI declarations')
need("_clean_name(title).casefold() not in {'spotify','spotify music','spotify premium','spotify free'}" in h13,
     'Spotify manual identity does not reject shell titles')
need("_clean_name(song).casefold() not in shell" in h13 and "return None,None" in h13,
     'Spotify auto identity is not GSMTC-only / shell-filtered')
need('def _h13_spotify_duration_witness' in h13 and
     "panel.media_sync._source_matches_process_hint(source, 'spotify.exe')" in h13,
     'Spotify source-affine duration witness missing')
need("spotify_duration = _h13_spotify_duration_witness(self, job.get('song',''), job.get('artist',''))" in h13 and
     "job['provider_duration_ms'] = spotify_duration" in h13,
     'Spotify automatic lyric fetch does not use player-owned duration across lyric providers')
need("request['provider_duration_ms']=_h13_spotify_duration_witness(self,song,artist)" in h13,
     'Spotify manual lyric fetch does not use player-owned duration across lyric providers')
need('LimbusLyric-H13SpotifyModeRefetch' in h13 and 'provider_duration_ms=_h13_spotify_duration_witness(self,song,artist)' in h13,
     'Spotify semantic mode refetch can still borrow lyric-provider timing')
need("spotify-gsmtc-primary" in h13 and "self._uia_reader.set_suspended(True" in h13,
     'Spotify does not explicitly suspend the UIA fallback worker')
need("source':'gsmtc-spotify-local'" in h13 and "confidence':1000" in h13,
     'Spotify local GSMTC clock publication missing')
need("source':'spotify-gsmtc-wait'" in h13, 'Spotify untrusted timeline does not fail closed')
need("MediaSessionSync._merge_uia_position = _h13_merge_uia_position" in h13 and
     "MediaSessionSync._guard_auto_local_handoff = _h13_guard_auto_local_handoff" in h13,
     'Spotify GSMTC clock is not isolated from legacy UIA/weak-handoff path')

# Three independent user lyric payload slots live beside song style data, not in provider scope.
need("H13_LYRIC_SLOT_NAMES = {" in h13, 'lyric slot map missing')
for slot in ("'precise': '精准'", "'classic': '经典'", "'translation': '仅翻译'"):
    need(slot in h13, f'missing fixed lyric slot: {slot}')
need("row.setdefault('lyric_slots', {})" in h13 or "row.setdefault('lyric_slots', {})" in h13.replace(' ', ''),
     'lyric slot storage missing')
need("'lyric_slots': {}" in h13, 'new song row does not carry lyric slots')
need("'user_owned': True" in h13, 'custom lyric result lacks user-owned metadata')
need("if not song or not artist:" in h13 and "identity = panel._track_identity(song, artist)" in h13 and
     "row = (getattr(panel, 'song_styles', {}) or {}).get(identity)" in h13,
     'custom lyric runtime lookup is not exact song+artist ownership')
need("row = {'song': song, 'artist': artist, 'rules': {}, 'mode': 'per_player', 'lyric_slots': {}}" in h13,
     'saving lyric content does not create an exact song+artist row')
for path_name in ('path=auto', 'path=manual', 'path=mode-refetch'):
    need(path_name in h13 and 'provider-network=skip' in h13, f'custom slot does not bypass provider on {path_name}')
need('ControlPanel._refetch_loaded_track_for_mode_switch = _h13_refetch_loaded_track_for_mode_switch' in h13,
     'semantic mode switch bypasses custom lyric slots')
need("panel._limbus_mode_payload_blocked = False" in h13,
     'saving a user slot does not release prior blank presentation ownership')
need("panel._refetch_loaded_track_for_mode_switch('h13-slot-delete')" in h13,
     'deleting active custom slot does not restore automatic semantic refetch')
need("time.monotonic()-started>=18.0" in h13 and 'late-result=stale-drop' in h13,
     'historical automatic lyric preview lacks bounded UI transaction')
need("LyricSearchEngine._set_cancel_check(cancel_check)" in h13 and
     "LyricSearchEngine._set_cancel_check(None)" in h13,
     'historical automatic lyric preview does not cooperatively retire stale provider work')

# Execute the pure mode mapper from source AST.
mode_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_h13_mode_slot_from_flags')
mod = ast.Module(body=[mode_node], type_ignores=[])
ns = {}
exec(compile(ast.fix_missing_locations(mod), '<h13-mode-map>', 'exec'), ns)
f = ns['_h13_mode_slot_from_flags']
need(f(False, True) == 'precise', 'precise slot mapping wrong')
need(f(False, False) == 'classic', 'classic slot mapping wrong')
need(f(True, True) == 'translation' and f(True, False) == 'translation', 'translation must dominate precision')

# OBS mirror is presentation-only and may never create/own transport state.
class_node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'H13ObsLyricMirror')
obs = ast.get_source_segment(text, class_node) or ''
need('MediaSessionSync' not in obs and 'media_sync' not in obs,
     'OBS mirror owns or reads MediaSync state')
need("self.setWindowTitle('LimbusLyric OBS Lyrics')" in obs, 'OBS capture window has no stable title')
need('self.source_window' in obs and 'src._current_visual_region().boundingRect()' in obs and 'src.grab(rect)' in obs,
     'OBS mirror is not driven from bounded presentation pixels')
need('setInterval(50)' in obs, 'OBS mirror first version exceeds the 20fps capture budget')
need('self.source_window.windowOpacity()' in obs, 'OBS mirror ignores the configured lyric opacity')
need("_h13_register_scale_baseline(self,card)" in h13, 'H13 controls are missing from the H12 UI scaling baseline')
need('已阻止跨歌曲复制歌词' in h13 and '_h13_copy_current_lyric_to_slot_editor' in h13,
     'historical DIY selection can copy the currently playing lyrics into another song')
for mode in ("'normal'", "'obs'", "'exclude'"):
    need(mode in h13, f'unified output mode missing: {mode}')
need("addItem('OBS 独立输出','obs')" in h13 and "addItem('捕获排除','exclude')" in h13,
     'three-mode output selector missing')

print('OUTPUT DIY SPOTIFY H13 REPLAY: PASS')
print('  per-song precise/classic/translation ownership: PASS')
print('  OBS mirror presentation-only contract: PASS')
print('  Spotify strict local-GSMTC/no-OAuth contract: PASS')
