#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
main = next(root.glob('LimbusLyric_v1.8.9.133_*FOUNDATION_20260814.py'))
src = main.read_text(encoding='utf-8-sig')
tree = ast.parse(src)

def fn(name):
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return ast.get_source_segment(src, n) or ''
    raise AssertionError(f'missing function {name}')

visual = fn('_h34_kugou_visual_guard_step')
trans = fn('_h95f10f4_draw_active_translation')
trans_cold = fn('_h95f10f17_draw_active_translation_cache_only')
primary_cold = fn('_h95f10f17_draw_active_primary_cache_only')
plain_hist = fn('_h95f10f17_draw_plain_history_row')
cover = fn('_h95f10f4_request_art')
cover_tick = fn('_h95f10f4_cover_tick')
region = fn('_r22_region_ui')
center = fn('_r22_retire_center_frequency')
reorder = fn('_r22_reorder_appearance')
sticky = fn('_r22_sticky_preview_cards')

checks = {
    'kugou-large-drift-needs-four-proofs': 'H34_KUGOU_VISUAL_SECOND_PROOF_HITS = 4' in src,
    'kugou-large-drift-needs-long-span': 'H34_KUGOU_VISUAL_SECOND_PROOF_SPAN_MS = 1800.0' in src,
    'kugou-proof-compares-rail-pace-to-wallclock': 'abs(dp-dt)<=pace_tol' in visual and 'dt>=300.0' in visual,
    'translation-active-spatial-anchor-owned-by-primary': 'gx=ox+ax*cursor; gy=oy+ay*cursor' in trans and '+dx' not in trans and '+dy' not in trans,
    'translation-cold-spatial-anchor-owned-by-primary': 'gx=ox+ax*cursor; gy=oy+ay*cursor' in trans_cold and 'Primary row owns spatial motion' in trans_cold,
    'primary-cold-material-is-row-atomic': 'row_plain=any(' in primary_cold and 'sprite=None if row_plain' in primary_cold,
    'translation-cold-material-is-lane-atomic': 'lane_complete=' in trans_cold and 'else:' in trans_cold and 'painter.drawText' in trans_cold,
    'history-cold-fallback-is-row-draw': 'painter.drawText' in plain_hist and 'for i,ch' not in plain_hist,
    'cover-respects-negative-cache': "_h88_art_negative" in cover and "time.monotonic()<float(negative.get(str(key),0.0)" in cover,
    'cover-worker-is-latest-wins': "r22-latest-wins" in cover and "_h87_art_serial" in cover,
    'persisted-color-applies-before-network': 'r22-persisted-cover-color' in cover and 'r22-persisted-cover-color' in cover_tick,
    'region-renamed-and-explained': '字幕可出现范围' in region and '当前显示器宽/高' in region,
    'center-frequency-retired-neutral': 'slider.setValue(100)' in center and 'slider.hide()' in center,
    'appearance-order-layout-region-preset-font-material': "'基础表现','排版与布局','字幕可出现范围','样式预设','字体与轮廓','光与材质'" in reorder,
    'studio-preview-sticky': 'h80_studio_stage_host' in sticky and 'card.setParent(host)' in sticky,
    'legacy-preview-remains-separate': "=='legacy'" in fn('_r22_sync_preview'),
    'frontend-wrapper-count-preserved': sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id=='LyricWindow' and t.attr=='paintEvent' for t in n.targets)) >= 7,
}
failed = [k for k,v in checks.items() if not v]
if failed:
    print('RUNTIME POLISH R2.2: FAIL')
    for k in failed: print('  -', k)
    raise SystemExit(1)
print('RUNTIME POLISH R2.2: PASS')
for k in checks: print('  ', k)
