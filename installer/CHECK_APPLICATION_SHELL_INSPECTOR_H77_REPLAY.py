from pathlib import Path
import sys,re
if len(sys.argv)<2: raise SystemExit('usage: CHECK_APPLICATION_SHELL_INSPECTOR_H77_REPLAY.py <main.py>')
main=Path(sys.argv[1]); src=main.read_text(encoding='utf-8'); root=main.parent
def fail(m): raise SystemExit('H77 FAIL: '+m)
def need(tok,label=None):
    if tok not in src: fail('missing '+(label or tok))
need('+ APPLICATION SHELL + INSPECTOR SYSTEM H77','build tag')
need('# H77 application shell + inspector system','marker')
if not (src.rindex("if '_h76_activate_ui' in globals():") < src.rindex("if '_h77_activate_ui' in globals():")): fail('H77 must activate after H76 UI')
block=src[src.index('# H77 application shell + inspector system'):]
if '# H78 studio navigation + typographic layout' in block:
    block=block[:block.index('# H78 studio navigation + typographic layout')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync','LyricSearchEngine','FadingLine','fading_lines','begin_fade','threading.Thread','QImage','QPixmap.fromImage','win32gui','uiautomation'):
    if bad in block: fail('crossed presentation boundary: '+bad)
for tok in ("btn.setText('界面')", "btn.setToolTip('界面 · 控制面板缩放与背景')", "title = QLabel('界面')", "scale_name = QLabel('界面缩放')", "bg_title = QLabel('背景')"):
    if tok not in block: fail('interface utility incomplete: '+tok)
for tok in ('h12_scale_combo','background_check','background_strength_slider','_choose_background_image','_clear_background_image'):
    if tok not in block: fail('mature interface owner proxy missing '+tok)
for tok in ('h75_application_card','_h75_card_for_widget',"card.setProperty('h75SearchIgnore', True)",'card.hide()'):
    if tok not in block: fail('duplicate Settings surface not hidden via compatibility owner: '+tok)
for tok in ("panel.app_title.setText('LIMBUSLYRIC')","panel.manager_tag.setText('NOW PLAYING')", "setObjectName('heroTrackTitle')", "setObjectName('heroStatusBadge')"):
    if tok not in block: fail('Now Playing shell missing '+tok)
for tok in ('_h77_is_inspector_row','_h77_polish_inspector_card','h77RowDivider','inspectorLabel','inspectorValue','QSlider::groove:horizontal'):
    if tok not in block: fail('inspector grammar missing '+tok)
for tok in ("('PLAYBACK', 'APPEARANCE', 'MOTION', 'SYSTEM', 'SONG OVERRIDE')", 'workspaceKicker'):
    if tok not in block: fail('workspace editorial hierarchy missing '+tok)
if "('设置','应用行为、同步输出、画面与更新')" not in block: fail('Settings page meta still advertises duplicate interface/background surface')
for bad in ('load_all_config(', 'save_all_config(', "settings['h77", 'setdefault(\'settings\')'):
    if bad in block: fail('H77 must not create/migrate config ownership: '+bad)
if 'H76_UI_POPUP_ENTER_MS' not in block or 'H76_UI_POPUP_RISE_PX' not in block: fail('Interface flyout must reuse H76 motion grammar')
note=root/'APPLICATION_SHELL_INSPECTOR_H77_NOTE_20260905.md'
if not note.is_file(): fail('missing H77 note')
print('APPLICATION SHELL + INSPECTOR SYSTEM H77 REPLAY: PASS')
