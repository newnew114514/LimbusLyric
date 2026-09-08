from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_EDITORIAL_INSTRUMENT_UI_H73_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()
root=path.parent

def fail(msg): raise SystemExit('H73 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ EDITORIAL INSTRUMENT UI H73','build tag')
need('# H73 editorial instrument UI','H73 source marker')
need("if '_h73_activate_ui' in globals():",'H73 activation')
if not (src.rindex("if '_h72_activate_runtime' in globals():") < src.rindex("if '_h73_activate_ui' in globals():")):
    fail('H73 must activate after H72')
for name in ('_h73_icon','_h73_strip_generation_prefix','_h73_show_background_popup','_h73_title_init','_h73_title_sync','_h73_panel_init','_h73_activate_ui'):
    fn(name)

block=src[src.index('# H73 editorial instrument UI'):]
if '# H74 preview stage + appearance inspector' in block:
    block=block[:block.index('# H74 preview stage + appearance inspector')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync.', 'LyricSearchEngine.', '_commit_seek', '_on_seek', 'win32gui.', 'threading.Thread(', 'QImage(', 'QPixmap.fromImage('):
    if bad in block: fail('H73 crossed presentation-only boundary: '+bad)

icon=fsrc('_h73_icon')
for tok in ("key == 'photo-edit'", "key == 'search'", "key == 'music'", "key == 'type'", "key == 'sparkles'", "key == 'disc'", "key == 'sliders'", "key == 'restore'"):
    if tok not in icon: fail('outline icon subset missing '+tok)
if 'QPixmap(size, size)' not in icon or 'QPainter(pm)' not in icon:
    fail('icons must stay dependency-free QPainter primitives')

popup=fsrc('_h73_show_background_popup')
for tok in ("QLabel('界面背景')", "QCheckBox('显示自定义背景')", "QPushButton('选择 / 更换')", "QPushButton('清除背景')", 'panel.background_strength_slider.setValue', 'panel._choose_background_image()', 'panel._clear_background_image()'):
    if tok not in popup: fail('background quick panel missing '+tok)

title=fsrc('_h73_title_init')
for tok in ("bar.build.setText('LYRIC STUDIO')", "setObjectName('titleUtilityButton')", "_h73_icon('photo-edit'", "host._h73_show_background_popup()", "btn.setText('')"):
    if tok not in title: fail('titlebar refinement missing '+tok)

panel=fsrc('_h73_panel_init')
for tok in ("('播放', '外观', '动效', '设置', '单曲')", 'H73_NAV_ORDER', "panel.mode_combo.setItemText(0, '完整字形')", "panel.mode_combo.setItemText(1, '轮廓余韵')", "label.setText('退场质感：')", '_h73_strip_generation_prefix(label)', "QLineEdit.LeadingPosition"):
    if tok not in panel: fail('semantic editor UI wiring missing '+tok)

# Config compatibility: stored renderer keys and tab indices are not rewritten.
if "addItem(\"中文\", \"chinese\")" not in src or "addItem(\"英文\", \"english\")" not in src:
    fail('legacy mode data keys changed')
if 'H73_NAV_ORDER = (0, 1, 2, 4, 3)' not in src:
    fail('visual nav order must not renumber underlying pages')

for note in ('EDITORIAL_INSTRUMENT_UI_H73_NOTE_20260905.md','THIRD_PARTY_UI_ICONS_H73.md'):
    p=root/note
    if not p.is_file(): fail('missing note '+note)
license_text=(root/'THIRD_PARTY_UI_ICONS_H73.md').read_text(encoding='utf-8')
if 'Tabler Icons' not in license_text or 'MIT' not in license_text:
    fail('third-party icon attribution incomplete')

print('EDITORIAL INSTRUMENT UI H73 REPLAY: PASS')
print(' - title bar uses dependency-free outline controls plus a discoverable background utility popup')
print(' - navigation/product language is Playback / Appearance / Motion / Song / Settings without tab-index migration')
print(' - renderer language switch is presented as glyph-exit texture, not Chinese/English language mode')
print(' - Hxx generation prefixes are removed from product-facing section headings only')
print(' - H73 remains presentation-only and adds no SVG/font/runtime packaging dependency')
