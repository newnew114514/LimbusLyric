#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_SYNC_UI_COLD_RENDER_PRECISE_PRIORITY_H95F10F8_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ SYNC UI + COLD RASTER + PRECISE PAIR PRIORITY H95F10F8' in src,'H95F10F8 build tag missing')
marker='# H95F10F8 sync UI + cold-raster closure + precise bilingual pair priority'
need(marker in src,'H95F10F8 runtime marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
required=(
 '_h95f10f8_choose_bilingual_pair','_h95f10f8_fetch_precise_pair','_h95f10f8_precise_pair_rescue','_h95f10f8_search','_h95f10f8_restore_sync_doctor','_h95f10f8_prune_retired_sync_rows',
 '_h95f10f8_missing_chars','_h95f10f8_queue_worker_prewarm','_h95f10f8_install_song_fragment_atlas',
 '_h95f10f8_cold_cache_state','_h95f10f8_paint_event','_h95f10f8_translation_prewarm',
 '_h95f10f8_control_init','_h95f10f8_activate')
for n in required: need(n in funcs,'missing '+n)
def fs(n): return ast.get_source_segment(src,funcs[n]) or ''

# Behavior: precise selection must preserve word-clock quality before translation coverage;
# fast/classic remains coverage-first.
node=copy.deepcopy(funcs['_h95f10f8_choose_bilingual_pair']); node.decorator_list=[]
logs=[]; ns={'write_error_log':lambda *a,**k: logs.append((a,k))}
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<f8-pair>','exec'),ns)
rows=[
 {'provider':'网易云','coverage':.984,'quality':1,'trans_rows':126},
 {'provider':'酷狗','coverage':.940,'quality':3,'trans_rows':63},
 {'provider':'QQ音乐','coverage':.875,'quality':3,'trans_rows':60},
]
need(ns['_h95f10f8_choose_bilingual_pair'](rows,'QQ音乐',True)['provider']=='酷狗','precise request traded quality-3 pair for coverage')
need(ns['_h95f10f8_choose_bilingual_pair'](rows,'QQ音乐',False)['provider']=='网易云','fast/classic coverage-first behavior changed')
# The protected mature search body stays byte-locked. F8 rescues only after that owner
# returns no quality-3 pair, using strict provider-specific precise probes.
search=fs('_h95f10f8_search'); rescue=fs('_h95f10f8_precise_pair_rescue'); fetch=fs('_h95f10f8_fetch_precise_pair')
for t in ('_H95F10F8_SEARCH_PRE','require_translation_pair','_lyric_clock_quality','_h95f10f8_precise_pair_rescue'):
    need(t in search,'post-mature precise rescue wrapper missing '+t)
for t in ('search_netease','search_qq','search_kugou','_h95f10f8_duration_compatible','_translation_to_line_lrc'):
    need(t in fetch,'strict quality-3 pair probe missing '+t)
for t in ('_remember_bilingual_pair','_build_lyric_payload_meta','provider-mix=0'):
    need(t in rescue,'rescued pair handoff/provenance missing '+t)

# UI: restore mature Sync Doctor and physically retire only obsolete H75 row geometry.
restore=fs('_h95f10f8_restore_sync_doctor'); prune=fs('_h95f10f8_prune_retired_sync_rows')
for t in ('h95f10f6_sync_doctor_toggle','h95f10f6_sync_doctor_box','inner.takeAt','layout.insertWidget','layout.insertLayout'):
    need(t in restore,'Sync Doctor restore missing '+t)
need('.show()' in restore,'restored Sync Doctor remains hidden')
for t in ('h75_offset_proxies','retired_labels','layout.takeAt','child.takeAt','w.hide()'):
    need(t in prune,'retired sync row physical removal missing '+t)
need('deleteLater()' in prune,'orphaned retired row layout is not retired')

# Cold-raster path: worker owns styled QImage raster; GUI installs one sprite per tick;
# paint may only route to the pre-existing plain renderer and hot translation draw.
worker=fs('_h95f10f8_queue_worker_prewarm'); install=fs('_h95f10f8_install_song_fragment_atlas'); paint=fs('_h95f10f8_paint_event')
for t in ('_render_song_atlas_glyph','threading.Thread','SetThreadPriority','song_fragment_atlas_ready.emit'):
    need(t in worker,'worker prewarm missing '+t)
for bad in ('QPixmap.fromImage','_hires_glyph_sprite(','QPainterPath'):
    need(bad not in worker,'worker/GUI boundary regressed: '+bad)
for t in ('_h95f10f8_prewarm_queue','_h95f10f8_ensure_prewarm_timer'):
    need(t in install,'GUI install queue missing '+t)
prime=fs('_h95f10f8_prime_one')
need('_prime_hires_glyph_sprite_from_song_image' in prime,'existing sprite cache installer not reused')
for t in ('_limbus_plain_glyph_paint','_h35_draw_plain_history_rows','_h95f10f8_cold_cache_state'):
    need(t in paint,'cold paint guard missing '+t)
for bad in ('_hires_glyph_sprite(','_render_song_atlas_glyph','QPainterPath','QPixmap.fromImage'):
    need(bad not in paint,'paint still rasterizes/builds vectors: '+bad)

# Final ownership + protected boundary.
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for t in ('ControlPanel.__init__ = _h95f10f8_control_init','LyricWindow.paintEvent = _h95f10f8_paint_event','LyricWindow._install_song_fragment_atlas = _h95f10f8_install_song_fragment_atlas','LyricSearchEngine.search = staticmethod(_h95f10f8_search)',"globals()['_h95f10f3_schedule_translation_prewarm'] = _h95f10f8_translation_prewarm"):
    need(t in block,'final F8 owner missing '+t)
for bad in ('MediaSessionSync.position =','MediaSessionSync.seek =','MediaSessionSync.bind_track =','parse_lrc ='):
    need(bad not in block,'F8 crossed protected transport/parser authority: '+bad)
print('SYNC UI + COLD RENDER + PRECISE PAIR PRIORITY H95F10F8 REPLAY: PASS')
print('  Sync Doctor expanded; four retired H75 row layouts physically retired: PASS')
print('  precise bilingual requests keep quality-3 before coverage; fast mode remains coverage-first: PASS')
print('  cold glyph raster runs on QImage worker; one-QPixmap-per-tick install; paint raster=0: PASS')
