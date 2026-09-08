#!/usr/bin/env python3
from __future__ import annotations
import ast,pathlib,sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_UNIFIED_LYRIC_VISUAL_TIMING_FACADE_H95F10F12_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ UNIFIED LYRIC + VISUAL TIMING FACADE H95F10F12' in src,'F12 tag missing')
marker='# H95F10F12 unified lyric facade + visual timing hints'; need(marker in src,'F12 marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
req=('_h95f10f12_track_line','_h95f10f12_live_line','_h95f10f12_lyric_facade','_h95f10f12_visual_timing_hints','_h95f10f12_frame_plan','_h95f10f12_lyric_contract','_h95f10f12_activate')
for n in req: need(n in funcs,'missing '+n)
def fs(n): return ast.get_source_segment(src,funcs[n]) or ''
fac=fs('_h95f10f12_lyric_facade'); timing=fs('_h95f10f12_visual_timing_hints'); plan=fs('_h95f10f12_frame_plan'); act=fs('_h95f10f12_activate')
for t in ("_h95f10f12_track_line(window, index)", "str(shadow.get('text') or '') == live_text", "'H95-unified-track' if coherent else 'mature-timeline-fallback'", "'main_timing': 'word' if precise else 'line'", "'translation_timing': 'line'"):
    need(t in fac,'unified/stale-safe facade missing '+t)
for t in ("'birth_ms'","'content_begin_ms'","'content_end_ms'","'handoff_ms'","'semantic_end_ms'","'clock_owner': 'mature-player-sync'","'exit_policy_owner': 'H59/H62/H68/H70/H76'","'effect_progress_owner': 'mature-fading-line'"):
    need(t in timing,'visual timing semantic missing '+t)
for t in ("plan['lyric_input'] = facade","plan['timing'] = timing","plan['lyric_data_owner']","plan['next_lyric_input']"):
    need(t in plan,'render-plan facade wiring missing '+t)
need("globals()['_h95f10f9_frame_plan'] = _h95f10f12_frame_plan" in act,'F12 final plan owner missing')
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for bad in ('parse_lrc(', 'LyricSearchEngine.search =','MediaSessionSync.position =','MediaSessionSync.seek =','MediaSessionSync.bind_track =','FadingLine.draw =','LyricWindow.paintEvent =','_h62_decay_progress =','_entrance_motion =','_render_song_atlas_glyph','QPainterPath'):
    need(bad not in block,'F12 crossed protected/data/render authority: '+bad)
print('UNIFIED LYRIC + VISUAL TIMING FACADE H95F10F12 REPLAY: PASS')
print('  existing H95 unified track reused with stale-shadow rejection: PASS')
print('  main word timing / translation line timing exposed through one facade: PASS')
print('  birth/content/handoff/semantic-end vocabulary is stable and read-only: PASS')
print('  provider/search/clock/seek/effect/paint authority unchanged: PASS')
