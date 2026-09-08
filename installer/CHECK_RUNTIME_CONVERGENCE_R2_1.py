#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys

root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
main=next(root.glob('LimbusLyric_v1.8.9.133_*FOUNDATION_20260814.py'))
src=main.read_text(encoding='utf-8-sig')
tree=ast.parse(src)

def method(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for x in n.body:
                if isinstance(x,ast.FunctionDef) and x.name==name:
                    return ast.get_source_segment(src,x) or ''
    raise AssertionError(f'missing {cls}.{name}')

auto=method('ControlPanel','_start_auto_search_job')
advance=method('MediaSessionSync','_kugou_advance_transport_generation')
commit=method('MediaSessionSync','_kugou_commit_gesture_seek')

checks={
 'fast-main-does-not-wait-bilingual-pair': 'require_translation_pair=False' in auto,
 'search-enrichment-is-local-only': 'search_artist = str(wart).strip()' in auto and "job['artist'] = str(wart).strip()" not in auto,
 'result-preserves-transport-identity': "result['search_identity_only'] = True" in auto,
 'burst-debounce-has-no-first-start-tax': "_r21_prev_start" in auto and "_r21_gap_ms < 1200.0" in auto and "network-started=0" in auto,
 'transport-edge-clears-hook-gesture': "_kugou_clear_inactive_mouse_events('transport-generation-change')" in advance,
 'transport-edge-clears-poll-gesture': '_h32_kugou_poll_start = None' in advance,
 'queued-pre-edge-gesture-rejected': 'R2.1酷狗跨Transport旧手势丢弃' in commit and '_r21_kugou_transport_generation_mono' in commit,
 'frontend-paint-chain-not-consolidated': sum(1 for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='LyricWindow' and t.attr=='paintEvent' for t in n.targets)) >= 7,
}
failed=[k for k,v in checks.items() if not v]
if failed:
    print('RUNTIME CONVERGENCE R2.1: FAIL')
    for k in failed: print('  -',k)
    raise SystemExit(1)
print('RUNTIME CONVERGENCE R2.1: PASS')
for k in checks: print('  ',k)
