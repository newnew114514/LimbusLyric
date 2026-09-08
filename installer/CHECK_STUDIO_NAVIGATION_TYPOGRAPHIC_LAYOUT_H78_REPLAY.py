from pathlib import Path
import sys,re
if len(sys.argv)<2: raise SystemExit('usage: CHECK_STUDIO_NAVIGATION_TYPOGRAPHIC_LAYOUT_H78_REPLAY.py <main.py>')
main=Path(sys.argv[1]); src=main.read_text(encoding='utf-8'); root=main.parent
def fail(m): raise SystemExit('H78 FAIL: '+m)
def need(tok,label=None):
    if tok not in src: fail('missing '+(label or tok))
need('+ STUDIO NAVIGATION + TYPOGRAPHIC LAYOUT H78','build tag')
need('# H78 studio navigation + typographic layout','marker')
if not (src.rindex("if '_h77_activate_ui' in globals():") < src.rindex("if '_h78_activate_ui' in globals():")): fail('H78 must activate after H77')
block=src[src.index('# H78 studio navigation + typographic layout'):]
if '# H79 live lyric shell + smooth snapshot transition' in block:
    block=block[:block.index('# H79 live lyric shell + smooth snapshot transition')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync','LyricSearchEngine','FadingLine','fading_lines','begin_fade','threading.Thread','QImage','QPixmap.fromImage','win32gui','uiautomation'):
    if bad in block: fail('crossed presentation boundary: '+bad)
for tok in ("btn.setText('界面')", "btn.setToolTip('界面 · 控制面板缩放、背景与显示')", 'global _h76_sync_background_button', '_h76_sync_background_button = _h78_sync_interface_button'):
    if tok not in block: fail('Interface semantic closure missing '+tok)
for tok in ('_h78_rehome_typography_layout', "label.setText('排版与布局')", "label.setText('语言字体')", "panel.main_tabs.widget(1).widget()", 'settings_layout.removeWidget(card)', 'appearance_layout.insertWidget(insert_at, card)'):
    if tok not in block: fail('H51 Appearance re-home missing '+tok)
for tok in ('h51_center_slider', 'h75SearchIgnore', "('外观','实时预览、字体、排版、布局、色彩与光效')", "('设置','应用行为、同步输出与更新')"):
    if tok not in block: fail('information architecture closure missing '+tok)
# Motion must be materially visible, not the old 0.84/165 ms token.
def const(name):
    m=re.search(r'^'+re.escape(name)+r'\s*=\s*([0-9.]+)', block, re.M)
    if not m: fail('missing constant '+name)
    return float(m.group(1))
if const('H78_PAGE_TRANSITION_MS') < 220: fail('page transition still too short')
if const('H78_PAGE_START_OPACITY') > 0.60: fail('page transition still too optically subtle')
if const('H78_NAV_INDICATOR_MS') < 180: fail('navigation indicator transition too short')
for tok in ('h78NavIndicator', "QPropertyAnimation(indicator, b'geometry'", '_h78_move_nav_indicator', "QGraphicsOpacityEffect(page)", "QGraphicsOpacityEffect(header)"):
    if tok not in block: fail('studio motion grammar missing '+tok)
for tok in ('h78WorkspaceMark', "kicker.setText(f'{idx+1:02d}  /  {word}'"):
    if tok not in block: fail('editorial workspace hierarchy missing '+tok)
for bad in ('load_all_config(', 'save_all_config(', "settings['h78", "setdefault('settings')"):
    if bad in block: fail('H78 must not create/migrate config ownership: '+bad)
note=root/'STUDIO_NAVIGATION_TYPOGRAPHIC_LAYOUT_H78_NOTE_20260905.md'
if not note.is_file(): fail('missing H78 note')
print('STUDIO NAVIGATION + TYPOGRAPHIC LAYOUT H78 REPLAY: PASS')
