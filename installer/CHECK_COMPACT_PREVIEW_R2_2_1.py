#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
main=next(root.glob('LimbusLyric_v1.8.9.133_*FOUNDATION_20260814.py'))
src=main.read_text(encoding='utf-8-sig'); tree=ast.parse(src)
def fn(name):
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name:
            return ast.get_source_segment(src,n) or ''
    raise AssertionError('missing '+name)
compact=fn('_r221_compact_preview'); activate=fn('_r221_activate_compact_preview')
checks={
 'studio-shell-preview-host-retired': "host.setMinimumHeight(0)" in compact and "host.setMaximumHeight(0)" in compact and "host.hide()" in compact,
 'preview-cards-rehomed-page-local': "_h95f4f3_rehome_preview_cards(panel)" in compact and "_h95f4f3_preview_rehomed=False" in compact,
 'compact-disclosure-buttons-restored': "btn.show()" in compact and "btn.setText('预览')" in compact,
 'mature-disclosure-state-reused': "_h95f4f3_apply_preview_state" in compact,
 'persisted-open-state-respected': "_h89_preview_open" in compact and "=False" not in compact.split("_h89_preview_open",1)[0][-80:],
 'motion-preview-replay-only-when-open': "idx==2 and bool(getattr(panel,'_h89_preview_open',False))" in compact,
 'studio-sync-routed-to-compact-preview': "_r22_sync_preview=_r221_compact_preview" in activate and "_h80_sync_studio_stage=_r221_compact_preview" in activate,
 'no-new-controlpanel-wrapper': 'ControlPanel.__init__' not in compact+activate,
}
failed=[k for k,v in checks.items() if not v]
if failed:
 print('COMPACT PREVIEW R2.2.1: FAIL')
 for k in failed: print('  -',k)
 raise SystemExit(1)
print('COMPACT PREVIEW R2.2.1: PASS')
for k in checks: print('  ',k)
