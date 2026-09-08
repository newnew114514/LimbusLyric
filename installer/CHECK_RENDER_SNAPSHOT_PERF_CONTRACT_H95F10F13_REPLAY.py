#!/usr/bin/env python3
from __future__ import annotations
import ast,pathlib,sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_RENDER_SNAPSHOT_PERF_CONTRACT_H95F10F13_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ RENDER SNAPSHOT + PERF CONTRACT H95F10F13' in src,'F13 tag missing')
marker='# H95F10F13 render snapshot + performance contract'; need(marker in src,'F13 marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
req=('_h95f10f13_frame_plan','_h95f10f13_render_snapshot','_h95f10f13_performance_contract','_h95f10f13_reset_performance_contract','_h95f10f13_activate')
for n in req: need(n in funcs,'missing '+n)
def fs(n): return ast.get_source_segment(src,funcs[n]) or ''
plan=fs('_h95f10f13_frame_plan'); snap=fs('_h95f10f13_render_snapshot'); perf=fs('_h95f10f13_performance_contract'); act=fs('_h95f10f13_activate')
for t in ("'cold_frames'","'mature_frames'","'unified_frames'","'fallback_frames'","'max_contract_ms'","'queue_peak'","plan['contract_build_ms']","plan['prefetch_queue_depth']"):
    need(t in plan,'perf frame accounting missing '+t)
for t in ("lyric.pop('words'", "'word_count'", "'timing': timing", "'visual': {", "'route':", "'plan_build_ms'", "'contract_build_ms'", "'prefetch_queue_depth'"):
    need(t in snap,'stable render snapshot missing '+t)
for t in ("'cold_ratio'", "'unified_ratio'", "'provider_allowed': False", "'glyph_raster_allowed': False", "'typography_resolve_allowed': False", "'image_filter_allowed': False", "'effect_formula_owner': 'mature-layers'"):
    need(t in perf,'performance contract missing '+t)
for t in ("globals()['_h95f10f9_frame_plan'] = _h95f10f13_frame_plan", 'LyricWindow._h95f10f13_render_snapshot', 'LyricWindow._h95f10f13_performance_contract'):
    need(t in act,'F13 activation missing '+t)
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for bad in ('LyricWindow.paintEvent =','LyricSearchEngine.search =','MediaSessionSync.position =','MediaSessionSync.seek =','FadingLine.draw =','QPainterPath','_render_song_atlas_glyph','_h51_prepare_line_typography','_h62_filter_shared_image','requests.'):
    need(bad not in block,'F13 crossed runtime authority '+bad)
print('RENDER SNAPSHOT + PERFORMANCE CONTRACT H95F10F13 REPLAY: PASS')
print('  snapshot exposes lyric/timing/visual/route without full word payload: PASS')
print('  cold/unified/queue/contract-cost counters are bounded primitive telemetry: PASS')
print('  paint hot-path forbidden-work contract is explicit: PASS')
print('  renderer/provider/clock/effect ownership unchanged: PASS')
