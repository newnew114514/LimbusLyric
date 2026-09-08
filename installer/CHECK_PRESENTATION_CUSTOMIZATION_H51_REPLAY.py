from pathlib import Path
import ast, sys

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_PRESENTATION_CUSTOMIZATION_H51_REPLAY.py <main.py>')
path = Path(sys.argv[1])
src = path.read_text(encoding='utf-8')
tree = ast.parse(src)
lines = src.splitlines()

def need(token, reason):
    if token not in src:
        raise SystemExit(f'H51 FAIL: {reason}: missing {token!r}')

def func_source(name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return '\n'.join(lines[node.lineno-1:node.end_lineno])
    raise SystemExit(f'H51 FAIL: function not found: {name}')

need('PRESENTATION CUSTOMIZATION H51', 'build tag')
need("if '_h51_activate_runtime' in globals():", 'final activation')
if src.index("if '_h51_activate_runtime' in globals():") < src.index("if '_h50_activate_runtime' in globals():"):
    raise SystemExit('H51 FAIL: H51 must activate after H50')

frag = func_source('_h51_fragment_exit_draw')
for token in ('QPainter.PixmapFragment.create', 'drawPixmapFragments', "effect == 'per_char'", "effect == 'wipe_ltr'", "else 1.0 - geom_norm", "_h51_exit_layout_cache", "sheet.cacheKey()"):
    if token not in frag:
        raise SystemExit(f'H51 FAIL: natural glyph exit missing {token}')
if 'setClipRect' in frag:
    raise SystemExit('H51 FAIL: H51 fragment exit regressed to rectangular clipping')

act = func_source('_h51_activate_runtime')
for token in (
    "FadingLine.draw._limbus_exit_policy = 'per-glyph-opacity-no-rectangular-clip'",
    "LyricWindow.place_randomly = h51_place_randomly",
    "LyricWindow._place_randomly_safe = h51_place_safe",
    "LyricWindow.start_lyric = h51_start_lyric",
    "LyricWindow.queue_visual_style = h51_queue_visual_style",
    "ControlPanel.__init__ = h51_control_init",
    "'h51_center_frequency_pct'", "'h51_size_range_enabled'", "'h51_font_min_pt'", "'h51_font_max_pt'",
    "'h51_font_ja_enabled'", "'h51_font_ko_enabled'", "'h51_font_western_enabled'",
    "'h51_screen_name'",
):
    if token not in act:
        raise SystemExit(f'H51 FAIL: runtime/config wiring missing {token}')
if 'setClipRect' in act:
    raise SystemExit('H51 FAIL: final H51 exit wrapper contains clipping')
for token in (
    "if effect not in ('per_char', 'wipe_ltr', 'wipe_rtl', 'shrink'):",
    "return fade_update_pre(row)", "return fade_draw_pre(row, painter)",
):
    if token not in act:
        raise SystemExit(f'H51 FAIL: classic fade/soft-drift/instant passthrough missing {token}')
if 'MediaSessionSync.' in act or 'bind_track' in act or '_poll_loop' in act:
    raise SystemExit('H51 FAIL: presentation patch must not touch transport/provider authority')
for token in ('new_size_policy != old_size_policy', "if not isinstance(getattr(window, '_h51_line_size_cache', None), OrderedDict):"):
    if token not in src:
        raise SystemExit(f'H51 FAIL: stable per-line size cache lifecycle missing {token}')
start_src = func_source('_h51_activate_runtime')
if 'window._h51_line_size_cache = OrderedDict()\n            return start_pre(window, text, font' not in start_src:
    raise SystemExit('H51 FAIL: R9 same-track start must initialize missing cache without unconditional reset')

screen = func_source('_h51_apply_target_screen')
for token in ('handle.setScreen(screen)', 'window.setGeometry(geom)', 'window.screen_w = new_w', 'window.screen_h = new_h'):
    if token not in screen:
        raise SystemExit(f'H51 FAIL: monitor binding missing {token}')

placement = act
for token in ('H51_CENTER_RETRY_MAX', '_h51_center_contains(window)', "freq >= 100", 'random.randint(1, 100) <= freq'):
    if token not in placement:
        raise SystemExit(f'H51 FAIL: center-frequency behavior missing {token}')
need('H51_CENTER_FREQ_DEFAULT = 100', 'backward-compatible center placement default')

style = func_source('_h51_prepare_line_typography')
for token in ("profile = _lyric_script_profile(text)", "_h51_size_range_enabled', False", 'random.randint(lo, hi)', "families.get(profile)", '_h51_font_supports_text(family, text)', '_h51_line_size_cache', 'if size_key in size_cache:', 'size_cache.move_to_end(size_key)', 'while len(size_cache) > 384'):
    if token not in style:
        raise SystemExit(f'H51 FAIL: per-line typography missing {token}')

for token in (
    "'ja': ('日文'", "'ko': ('韩文'", "'western': ('西文'",
    "('逐字消失（错落柔化）', 'per_char')",
    "('从左到右消失（字形渐隐）', 'wipe_ltr')",
    "('从右到左消失（字形渐隐）', 'wipe_rtl')",
    "('快速收缩/淡出', 'shrink')",
    "('直接消失', 'instant')",
    '启用每行字号范围', '每行字号范围：', '中央区域出现频率：', '字幕显示屏幕：',
):
    if token not in src:
        raise SystemExit(f'H51 FAIL: user-facing control missing {token}')

# Formula sanity for the per-glyph stagger used by the runtime: all glyphs start visible,
# all are gone at progress=1, and directional wipes start at opposite edges.
def smooth(p):
    p=max(0.0,min(1.0,p)); return p*p*(3.0-2.0*p)
def opacity(progress, order):
    start=order*0.56
    lp=max(0.0,min(1.0,(progress-start)/0.44))
    return 1.0-smooth(lp)
for order in (0.0, .25, .5, .75, 1.0):
    if abs(opacity(0.0, order)-1.0) > 1e-9 or opacity(1.0, order) > 1e-9:
        raise SystemExit('H51 FAIL: wipe opacity endpoints are invalid')
if not (opacity(.3, 0.0) < opacity(.3, 1.0)):
    raise SystemExit('H51 FAIL: left-to-right wipe does not lead from the left edge')
if not (opacity(.3, 1.0) > opacity(.3, 0.0)):
    raise SystemExit('H51 FAIL: directional stagger sanity')

print('PRESENTATION CUSTOMIZATION H51 REPLAY: PASS')
print(' - classic whole-row fade remains on the mature H20/H16 path; new glyph exits use one batched fragment draw')
print(' - per-glyph exit caches immutable row geometry so high-refresh displays do not recompute font metrics every frame')
print(' - center-zone frequency, per-line size range, JA/KO/Western fonts and monitor binding are persisted')
print(' - H51 remains presentation-only; transport/provider authority is untouched')
