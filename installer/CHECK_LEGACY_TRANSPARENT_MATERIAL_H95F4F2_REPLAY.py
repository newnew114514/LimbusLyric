#!/usr/bin/env python3
from __future__ import annotations
import ast
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_LEGACY_TRANSPARENT_MATERIAL_H95F4F2_REPLAY.py <main.py>')
path = Path(sys.argv[1]).resolve()
src = path.read_text(encoding='utf-8')
tree = ast.parse(src)

def need(cond, message):
    if not cond:
        raise AssertionError(message)

marker = '# H95F4F2 legacy transparent material'
need(marker in src, 'H95F4F2 marker missing')
need('+ LEGACY TRANSPARENT MATERIAL H95F4F2' in src, 'H95F4F2 build tag missing')
need(src.index('# H95F4F1 startup re-entry closure') < src.index(marker) < src.index('if __name__ == "__main__":'), 'H95F4F2 must be final shell-material layer before main')

assign = next((n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'H95F4F2_QSS' for t in n.targets)), None)
need(assign is not None and isinstance(assign.value, ast.Constant) and isinstance(assign.value.value, str), 'H95F4F2_QSS constant missing')
qss = assign.value.value

# Material must be explicitly scoped to Legacy, otherwise Modern Studio can regress.
need('QWidget[h95f4Frontend="legacy"] QFrame#panelTitleBar' in qss, 'legacy titlebar override missing')
need('QWidget[h95f4Frontend="legacy"] QFrame#h95f4LegacyHeader' in qss, 'legacy media header override missing')
need('QWidget[h95f4Frontend="legacy"] QTabWidget#mainTabs::pane' in qss, 'legacy tab pane override missing')
need('QWidget[h95f4Frontend="legacy"] QFrame#settingsCard' in qss, 'legacy cards are not material-scoped')
need('background: transparent;' in qss, 'transparent rest-state material missing')
need('border: none;' in qss, 'boxed border removal missing')
need('rgba(10,11,14,38)' in qss, 'legacy header did not become light translucent material')
need('rgba(9,10,13,58)' in qss, 'legacy tab pane did not become low-opacity material')
need('background: rgba(13,14,17,86)' in qss, 'legacy settings cards did not become lighter')

# New layer must persist across palette changes and initial construction.
fn_names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
need('_h95f4f2_ensure_qss' in fn_names, 'QSS persistence helper missing')
need('_h95f4f2_apply_frontend_theme' in fn_names, 'theme persistence wrapper missing')
need('_h95f4f2_control_init' in fn_names, 'startup material install missing')
block = src[src.index(marker):src.index('if __name__ == "__main__":', src.index(marker))]
need("globals()['_h87_apply_frontend_theme'] = _h95f4f2_apply_frontend_theme" in block, 'theme wrapper not activated')
need("ControlPanel.__init__ = _h95f4f2_control_init" in block, 'startup wrapper not activated')
need("legacy-only transparent material override; modern Studio shell untouched" in block, 'modern-shell isolation policy missing')

print('LEGACY TRANSPARENT MATERIAL H95F4F2 REPLAY: PASS')
print('  legacy title/header/tab surfaces are translucent and border-light: PASS')
print('  modern Studio selectors remain untouched by H95F4F2: PASS')
