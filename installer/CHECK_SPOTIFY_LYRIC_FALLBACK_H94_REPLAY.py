from __future__ import annotations
import ast
import os
import re
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_SPOTIFY_LYRIC_FALLBACK_H94_REPLAY.py <main.py>')
path=Path(sys.argv[1])
src=path.read_text(encoding='utf-8')

def need(cond,msg):
    if not cond:
        raise AssertionError(msg)

need('+ SPOTIFY LYRIC FALLBACK H94' in src,'build tag missing H94')
need('# H94 Spotify lyric fallback' in src,'H94 marker missing')
h93=src.index('# H93 explicit workspace grip')
start=src.index('# H94 Spotify lyric fallback')
h95=src.index('# H95 unified lyric foundation',start)
process_entry=src.index('if __name__ == "__main__":',h95)
end=h95
need(h93 < start < end < process_entry, 'H94/H94F1 must remain between H93 and the later H95 feature family')
block=src[start:end]
for tok in (
    'H94_SPOTIFY_LYRIC_FALLBACK_ENABLED',
    "LIMBUSLYRIC_MUSIXMATCH_API_KEY",
    "LIMBUSLYRIC_SPOTIFY_SP_DC",
    "LIMBUSLYRIC_SPOTIFY_BEARER_TOKEN",
    'matcher.subtitle.get',
    'color-lyrics/v2/track',
    '_LIMBUS_H94_AUTO_RESULT_PRE = ControlPanel._on_auto_lyric_result',
    '_LIMBUS_H94_MANUAL_RESULT_PRE = ControlPanel._on_manual_lyric_result',
    '_LIMBUS_H94_MODE_RESULT_PRE = ControlPanel._on_mode_lyric_result',
):
    need(tok in block,'missing H94 token '+tok)
need("if bool(row.get('trans_only')) or bool(row.get('cancelled')):" in block and
     "if str(row.get('source') or '') not in LYRIC_SOURCE_ORDER:" in block and
     "if not str(row.get('song') or '').strip() or row.get('lyric'):" in block,
     'Spotify fallback can preempt successful/native/translation paths')
need('LyricSearchEngine.search =' not in block,
     'H94 illegally replaces H81-protected search authority')
need('_H94_ACTIVE_FALLBACK_LOCK = threading.Lock()' in block and '_H94_ACTIVE_FALLBACKS = set()' in block,
     'duplicate Spotify fallback requests are not transaction-deduplicated')
need('expected = _h94_selected_player_duration_for_fallback(panel, request)' in block and
     'expected_duration_ms=expected, path=path' in block,
     'selected-player duration is not frozen before the worker starts')
need("def _h94_prepare_result_payload(row, lrc, lyric_duration, meta, *, expected_duration_ms=0, path='auto'):" in block,
     'payload worker still depends on ControlPanel/QWidget state')
need('LyricSearchEngine._set_cancel_check(cancelled)' in block and 'LyricSearchEngine._set_cancel_check(None)' in block,
     'Spotify worker does not inherit/clear transaction cancellation')
for bad in (
    'MediaSessionSync._merge_uia_position =', 'MediaSessionSync.bind_track =',
    'AsyncPlayerUiPositionReader.poll =', 'LyricSearchEngine.search =',
    'FadingLine.update =', 'FadingLine.draw ='
):
    need(bad not in block, 'H94 crossed protected authority boundary: '+bad)
need('_h94_result_needs_spotify_fallback' in block and '_h94_fetch_spotify_lyric_fallback' in block,
     'result-layer final-empty fallback chain missing')
need("if bool(row.get('precision_upgrade_pending')) or bool(row.get('progressive_keep_fast')):" in block,
     'auto progressive intermediate/keep-fast rows can incorrectly trigger Spotify')
need("str(row.get('event') or '') != 'search-result' or not bool(row.get('final')) or bool(row.get('keep_fast'))" in block,
     'manual non-final/keep-fast rows can incorrectly trigger Spotify')
need("return _h94_spotify_color_lyrics(song_name, artist, expected_duration_ms)" in block,
     'documented Musixmatch -> internal Spotify ordering missing')
need('timeout=(H94_SPOTIFY_CONNECT_TIMEOUT, H94_SPOTIFY_READ_TIMEOUT)' in block,
     'H94 network path lacks bounded connect/read timeout')
need('credential_capture=0' in block and 'api_key_logged=0' in block,
     'credential non-logging diagnostics missing')
need('browser-cookie scraping' in block.lower() or 'browser credential' in block.lower(),
     'explicit no-cookie-scraping contract missing')
need("'transport_authority=0'" in block or 'transport_authority=0' in block,
     'lyric fallback does not explicitly deny transport authority')
need("sync_type != 'LINE_SYNCED'" in block,
     'internal Spotify unsynced payload could enter timed renderer')
need("elif not str(artist or '').strip():" in block,
     'Spotify fourth-provider identity gate accepts title-only/no-duration candidates')
need("duration_delta > max(3500" in block,
     'Spotify track version duration gate missing')
need("_clean_name(song).casefold() not in shell" in src and "if cls._process_stem(process_name)=='spotify': return True" in src,
     'H13 strict Spotify playback identity/affinity was lost')
need("return 'spotify' in str(source or '').replace('\\\\','/').lower()" in src or
     "return 'spotify' in str(source or '').replace('\\','/').lower()" in src,
     'Spotify source-affinity matcher missing')
need("if cls._process_stem(process_name)=='spotify': return True" in src,
     'Spotify is not a strict built-in GSMTC process')
def spotify_source_match(source):
    return 'spotify' in str(source or '').replace('\\','/').lower()
need(spotify_source_match('Spotify.exe'), 'desktop Spotify GSMTC source would be rejected')
need(spotify_source_match('SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify'), 'Store Spotify AUMID would be rejected')
need(not spotify_source_match('Microsoft.ZuneMusic_8wekyb3d8bbwe!Microsoft.ZuneMusic'),
     'unrelated GSMTC source would be accepted as Spotify')
need("import winrt.windows.foundation,winrt.windows.foundation.collections" in (path.parent/'installer'/'BUILD_RELEASE.cmd').read_text(encoding='ascii',errors='ignore'),
     'packaging no longer verifies WinRT dependency used by Spotify GSMTC')

# Execute pure conversion/scoring helpers with small stubs; no network.
tree=ast.parse(src)
names={'_h94_ms_to_lrc_tag','_h94_lrc_has_timed_rows','_h94_spotify_candidate_score'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
need({n.name for n in nodes}==names,'pure H94 helper definitions missing')
ns={'re':re}
ns['_clean_name']=lambda x: re.sub(r'[^a-z0-9]+','',str(x or '').lower())
def alias(a,b):
    aa=ns['_clean_name'](a); bb=ns['_clean_name'](b)
    return (bool(aa and bb and (aa==bb or aa in bb or bb in aa)), '')
ns['_artist_alias_match']=alias
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<h94-pure>','exec'),ns)
need(ns['_h94_ms_to_lrc_tag'](6990)=='[00:06.990]','millisecond LRC conversion wrong')
need(ns['_h94_lrc_has_timed_rows']('[00:01.230]x'),'timed LRC detector wrong')
row={'name':'Test Song','artists':[{'name':'Test Artist'}],'duration_ms':200000}
need(ns['_h94_spotify_candidate_score']('Test Song','Test Artist',201000,row) is not None,'safe candidate rejected')
need(ns['_h94_spotify_candidate_score']('Test Song','Other Artist',201000,row) is None,'wrong artist accepted')
need(ns['_h94_spotify_candidate_score']('Test Song','Test Artist',240000,row) is None,'wrong duration/version accepted')
need(ns['_h94_spotify_candidate_score']('Test Song','',0,row) is None,'title-only/no-duration candidate accepted')

# The old H13 gate must now scope its no-Web-API transport contract to H13 only.
h13gate=(path.parent/'installer'/'CHECK_OUTPUT_DIY_SPOTIFY_H13_REPLAY.py').read_text(encoding='utf-8')
need("h14 = text.index('# H14 auto-precision deadline / bounded enhancement')" in h13gate and 'h13 = text[start:h14]' in h13gate,
     'H13 replay still accidentally forbids all future lyric-only Spotify layers')

note=path.parent/'SPOTIFY_LYRIC_FALLBACK_H94_NOTE_20260906.md'
need(note.is_file(),'H94 note missing')
for tok in ('GSMTC','Musixmatch','color-lyrics','soft-fail','No new Python dependency'):
    need(tok in note.read_text(encoding='utf-8'),'H94 note missing '+tok)

print('SPOTIFY LYRIC FALLBACK H94 REPLAY: PASS')
print('  existing three-provider search remains untouched; result-layer final-empty fallback only: PASS')
print('  Musixmatch documented path + internal Spotify soft fallback: PASS')
print('  Spotify GSMTC transport authority remains H13-only: PASS')
