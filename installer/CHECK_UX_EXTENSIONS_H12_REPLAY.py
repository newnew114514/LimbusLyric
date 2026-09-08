from __future__ import annotations

import ast
import math
import random
import sys
import time
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_UX_EXTENSIONS_H12_REPLAY.py <main.py>')
path = Path(sys.argv[1])
text = path.read_text(encoding='utf-8')
ast.parse(text)

start = text.index('# H12 UX extensions')
end = text.index('\ndef _global_exception_hook', start)
h12 = text[start:end]

def need(cond, msg):
    if not cond:
        raise AssertionError(msg)

need('UX EXTENSIONS H12' in text.splitlines()[63], 'build tag missing H12')
for needle in (
    "for p in (100,110,125,150)",
    "self.h12_opacity.setRange(0,100)",
    "self.h12_weight.setRange(1,99)",
    "('整行淡出','fade')", "('逐字消失','per_char')", "('从左到右消失','wipe_ltr')",
    "('从右到左消失','wipe_rtl')", "('快速收缩/淡出','shrink')", "('直接消失','instant')",
    "歌词颜色跟随封面", "捕获排除", "检查更新", "下载更新",
):
    need(needle in h12, f'missing H12 contract: {needle}')

# Capture exclusion must never silently use the legacy WDA_MONITOR fallback.
need('WDA_MONITOR' not in h12, 'legacy WDA_MONITOR fallback present')
need("build<19041" in h12 and 'SetWindowDisplayAffinity' in h12 and ',0x11)' in h12,
     'capture exclusion lacks Windows 10 2004+ gate / WDA_EXCLUDEFROMCAPTURE')

# External navigation is HTTPS-only; H12 never overwrites the running EXE.
need("url.startswith('https://')" in h12, 'update endpoint is not HTTPS-gated')
need("dl if dl.startswith('https://') else ''" in h12, 'returned update URL is not HTTPS-filtered')
need("startswith('https://') else None" in h12, 'download/open action is not HTTPS-gated')
need('os.replace(' not in h12 and 'shutil.copy' not in h12, 'H12 must not self-overwrite executable')

# Cover result is bound to the current track and does not override DIY/random text color.
need("key==cur" in h12 and "_active.get('text_color')" in h12 and "_random.get('text_color')" in h12,
     'cover-follow ownership guard missing')
need("threading.Thread(target=work,name='LimbusLyric-H12Cover',daemon=True)" in h12,
     'cover lookup not daemon/background')
need("threading.Thread(target=work,name='LimbusLyric-H12Update',daemon=True)" in h12,
     'update check not daemon/background')
need("_h12_update_busy" in h12 and "if bool(getattr(panel,'_h12_update_busy',False)): return" in h12,
     'update check is not single-flight')
need("self.font_bold_check.toggled.connect(lambda on: self.h12_weight.setValue(75 if on else 50))" in h12,
     'legacy bold shortcut is not bridged to continuous weight')
need("ControlPanel.pick_color=_h12_pick_color" in h12 and "self.h12_cover_check.setChecked(False)" in h12,
     'manual color picker does not leave cover-follow mode after a real color change')

# Scaling must always derive from an immutable baseline rather than scale-on-scale.
need("_h12_stylesheet_base" in h12 and "_h12_widget_baseline" in h12 and "_h12_layout_baseline" in h12,
     'UI scale baselines missing')
need("factor=pct/100.0" in h12, 'UI scale factor missing')

# H12 must retain the original smooth simulator-style target interpolation.
need("return _LIMBUS_SHAKE_PRE_H12(states,intensity,cadence_ms,last_target_mono,last_motion_mono,now_mono)" in h12,
     'H12 no longer delegates to the smooth baseline shake')

# Run the baseline and H12 delegate from source AST.
tree = ast.parse(text)
base_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_advance_living_shake')
shake_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_h12_shake')
bind = ast.Assign(
    targets=[ast.Name(id='_LIMBUS_SHAKE_PRE_H12', ctx=ast.Store())],
    value=ast.Name(id='_advance_living_shake', ctx=ast.Load()),
)
mod = ast.Module(body=[base_node, bind, shake_node], type_ignores=[])
ns = {'math': math, 'random': random, 'time': time}
exec(compile(ast.fix_missing_locations(mod), '<h12-shake>', 'exec'), ns)
shake = ns['_h12_shake']
random.seed(7)
states = [{'x': 0.0, 'y': 0.0, 'target_x': 0.0, 'target_y': 0.0} for _ in range(24)]
now = 1000.0
last_target = 0.0
last_motion = 999.0
for step in range(120):
    now += 17.0
    _, last_target, last_motion = shake(states, 2, 143, last_target, last_motion, now)
    need(all(abs(float(s.get('x', 0))) <= 2.000001 and abs(float(s.get('y', 0))) <= 2.000001 for s in states),
         'smooth shake exceeded configured intensity')
need(not any('_h12_next_kick' in s for s in states), 'intermittent micro-jolt state leaked back in')

print('UX EXTENSIONS H12 REPLAY: PASS')
print('  scale/opacity/weight/exit/capture/update/cover contracts: PASS')
print('  simulator-style smooth shake delegation: PASS')
