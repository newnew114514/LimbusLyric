#!/usr/bin/env python3
from __future__ import annotations
import ast
import pathlib
import sys

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_UNIFIED_LYRIC_SYNC_DOCTOR_H95_REPLAY.py <main.py>')
path = pathlib.Path(sys.argv[1]).resolve()
src = path.read_text(encoding='utf-8')
tree = ast.parse(src)

def need(cond, msg):
    if not cond:
        raise AssertionError(msg)

need('# H95 unified lyric foundation + Sync Doctor V1' in src, 'H95 marker missing')
need('+ UNIFIED LYRIC FOUNDATION + SYNC DOCTOR H95' in src, 'build tag missing H95')
need("'sync_doctor_corrections': getattr(panel, '_h95_sync_doctor_store'" in src, 'song correction persistence missing')
need('timeline = parse_lrc(text, diagnostics=False)' in src, 'unified model no longer consumes the existing parser contract')
need('LyricWindow._playback_position = _h95_lyric_playback_position' in src, 'display-clock sidecar is not installed')
need("final-display-clock-only; no transport/source timestamp authority" in src, 'H95 transport-authority denial missing')
for bad in (
    'MediaSessionSync._merge_uia_position =', 'MediaSessionSync.bind_track =',
    'LyricSearchEngine.search =', 'parse_lrc = _h95', 'LyricWindow.start_lyric = _h95'
):
    _h95_start = src.index('# H95 unified lyric foundation + Sync Doctor V1')
    _h95_end = src.index('# H95F1 adaptive header + grip micro interaction + background frost', _h95_start)
    h95 = src[_h95_start:_h95_end]
    need(bad not in h95, 'H95 crossed protected ownership boundary: ' + bad)

wanted = {
    '_h95_clamp_int', '_h95_normalize_correction_row', '_h95_model_from_row',
    '_h95_correct_display_position', '_h95_unified_track_from_timeline'
}
nodes = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted}
need(set(nodes) == wanted, 'H95 pure helper definitions missing')
# Preserve source order for dependencies.
body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
ns = {
    'H95_SYNC_MAX_ABS_CORRECTION_MS': 5000,
    'H95_SYNC_MAX_ANCHORS': 8,
    'H95_SYNC_LINEAR_MIN_SPAN_MS': 15000,
    'H95_SYNC_LINEAR_MIN_SCALE': 0.98,
    'H95_SYNC_LINEAR_MAX_SCALE': 1.02,
    'H95_UNIFIED_MODEL_VERSION': 1,
}
exec(compile(ast.Module(body=body, type_ignores=[]), '<h95-pure>', 'exec'), ns)

# Quick manual adjustment remains a non-destructive translation.
row = {'song':'A','artist':'B','manual_adjust_ms':100,'anchors':[]}
final, delta, model = ns['_h95_correct_display_position'](10000, row)
need((final, delta, model['mode']) == (10100, 100, 'offset'), 'manual +100ms correction is wrong')

need("row['manual_adjust_ms'] = 0" in src, 'anchoring does not consolidate the existing manual nudge and can double-apply correction')

# One user anchor makes the currently chosen source line land exactly on that playback moment.
row = {'song':'A','artist':'B','manual_adjust_ms':0,'anchors':[{'playback_ms':10000,'source_ms':10500}]}
final, delta, model = ns['_h95_correct_display_position'](10000, row)
need(final == 10500 and delta == 500 and model['mode'] == 'offset', 'single-anchor offset model is wrong')

# Two widely separated anchors identify linear drift instead of collapsing to a fixed offset.
row = {'song':'A','artist':'B','manual_adjust_ms':0,'anchors':[
    {'playback_ms':10000,'source_ms':10200},
    {'playback_ms':110000,'source_ms':110400},
]}
final0, delta0, model = ns['_h95_correct_display_position'](10000, row)
final1, delta1, _ = ns['_h95_correct_display_position'](110000, row)
need(model['mode'] == 'linear', 'two distant anchors did not enable linear drift model')
need(abs(final0 - 10200) <= 1 and abs(final1 - 110400) <= 1, 'linear model does not honor anchors')
need(delta1 > delta0, 'drift correction does not evolve over playback time')

# Unsafe slope must fall back to translation instead of stretching the timeline wildly.
row = {'song':'A','artist':'B','manual_adjust_ms':0,'anchors':[
    {'playback_ms':10000,'source_ms':10000},
    {'playback_ms':110000,'source_ms':130000},
]}
_, _, model = ns['_h95_correct_display_position'](60000, row)
need(model['mode'] == 'offset', 'unsafe drift slope was accepted')

# Correction is hard-clamped even with hostile/corrupt persisted data.
row = {'song':'A','artist':'B','manual_adjust_ms':999999,'anchors':[]}
_, delta, _ = ns['_h95_correct_display_position'](10000, row)
need(abs(delta) <= 5000, 'correction clamp failed')

# Unified sidecar preserves line times and converts precise reveal slices into word/token events.
timeline = [
    (1000, 'hello world', [(1000,5,1400,0),(1500,11,2100,5)]),
    (3000, 'next', None),
]
track = ns['_h95_unified_track_from_timeline'](timeline, song='Song', artist='Artist', source='QQ音乐', identity='song|artist')
need(track['model_version'] == 1 and len(track['lines']) == 2, 'unified track shape wrong')
need(track['lines'][0]['start_ms'] == 1000 and track['lines'][1]['start_ms'] == 3000, 'line timestamps changed')
need([w['text'] for w in track['lines'][0]['words']] == ['hello', ' world'], 'precise token slices changed')
need(track['precise_line_count'] == 1 and track['word_event_count'] == 2, 'unified precision counters wrong')
need(all(line['role'] == 'MAIN' for line in track['lines']), 'H95 invented unsupported singer roles')
need(all(line['translation'] == '' and line['romanization'] == '' for line in track['lines']), 'H95 invented translation/romanization data')

# UI must expose the intended user actions without hiding source mutation behind them.
need("(('−100', -100), ('−50', -50), ('+50', 50), ('+100', 100))" in src, 'Sync Doctor quick-adjust buttons missing')
for token in ('这句现在才该出现','撤销锚点','清除本曲修正'):
    need(token in src, 'Sync Doctor UI action missing: ' + token)
need('不修改播放器位置' in src and '不改 QRC / LRC / 后续 TTML' in src, 'non-destructive UI contract missing')

print('UNIFIED LYRIC + SYNC DOCTOR H95 REPLAY: PASS')
print('  per-song offset + bounded linear drift model: PASS')
print('  shadow unified Track/Lines/Words adapter: PASS')
print('  transport/provider/source timestamp ownership unchanged: PASS')
