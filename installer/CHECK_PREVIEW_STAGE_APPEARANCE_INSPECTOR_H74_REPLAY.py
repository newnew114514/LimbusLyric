from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_PREVIEW_STAGE_APPEARANCE_INSPECTOR_H74_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines(); root=path.parent

def fail(msg): raise SystemExit('H74 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name: return node
    fail('function not found: '+name)
def cls(name):
    for node in ast.walk(tree):
        if isinstance(node,ast.ClassDef) and node.name==name: return node
    fail('class not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))
def csrc(name):
    n=cls(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ PREVIEW STAGE + APPEARANCE INSPECTOR H74','build tag')
need('# H74 preview stage + appearance inspector','source marker')
need("if '_h74_activate_ui' in globals():",'activation')
if not (src.rindex("if '_h73_activate_ui' in globals():") < src.rindex("if '_h74_activate_ui' in globals():")):
    fail('H74 must activate after H73')
for name in ('_h74_icon','_h74_clamp','_h74_profile','_h74_effect_duration','_h74_find_layout_for_widget','_h74_card_title','_h74_make_preview_card','_h74_bind_proxy_slider','_h74_install_appearance_inspector','_h74_install_preset_overflow','_h74_reorder_cards','_h74_refresh_previews','_h74_connect_previews','_h74_panel_init','_h74_activate_ui'):
    fn(name)
cls('H74PreviewStage')

block=src[src.index('# H74 preview stage + appearance inspector'):]
if '# H75 information architecture + Spotify parity' in block:
    block=block[:block.index('# H75 information architecture + Spotify parity')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync.', 'LyricSearchEngine.', '_commit_seek', '_on_seek', 'threading.Thread(', 'requests.', 'QImage(', 'QPixmap.fromImage(', '_discard_fading_item(', 'fading_lines.append(', 'history_lines.append('):
    if bad in block: fail('H74 crossed presentation-only boundary: '+bad)

stage=csrc('H74PreviewStage')
for tok in ("self.setObjectName('h74PreviewStage')", 'self._timer.setInterval(24)', 'self._replay_serial += 1', 'time.monotonic()', "text = text[:18]", "effect == 'per_char'", "effect in ('wipe_ltr', 'wipe_rtl')", "effect == 'blur_decay'", '_draw_soft_glow_path'):
    if tok not in stage: fail('preview-stage contract missing '+tok)
if 'MediaSessionSync' in stage or 'lyric_window.update(' in stage:
    fail('preview stage became a runtime/desktop authority')

card=fsrc('_h74_make_preview_card')
for tok in ("'实时预览' if mode == 'appearance' else '退场预览'", "QLineEdit(getattr(panel, '_h74_preview_text'", "replay.setText('重播')", 'panel.h74_motion_replay_btn.clicked.connect(stage.replay)'):
    if tok not in card: fail('preview-card UX missing '+tok)

inspector=fsrc('_h74_install_appearance_inspector')
for tok in ("QLabel('基础表现')", 'panel.h74_weight_slider', 'panel.h12_weight', 'panel.h74_opacity_slider', 'panel.h12_opacity', "QCheckBox('颜色跟随当前封面')", 'panel.h12_cover_check.setChecked', 'widget.hide()'):
    if tok not in inspector: fail('appearance inspector compatibility missing '+tok)

preset=fsrc('_h74_install_preset_overflow')
for tok in ("('+', '-', '更新', '重命名')", "menu.addAction('新建预设', panel.new_preset)", "menu.addAction('保存到当前预设', panel.update_preset)", "menu.addAction('重命名', panel.rename_preset)", "menu.addAction('删除当前预设', panel.delete_preset)"):
    if tok not in preset: fail('preset overflow missing '+tok)

panel=fsrc('_h74_panel_init')
for tok in ("style_layout.insertWidget(0, appearance_card)", "motion_layout.insertWidget(0, motion_card)", "('基础表现','样式预设','字体与轮廓','光与材质')", "('退场','入场','运动','空间方向','同步')", "('外观', '实时预览、字体、色彩、轮廓与光效')", "('动效', '实时预览、入场、退场与字符运动')"):
    if tok not in panel: fail('creative-first layout missing '+tok)

# The original H12 data owners must still exist in source and retain original config keys.
for tok in ("st.get('h12_lyric_opacity',100)", "st.get('h12_font_weight'", "self.h12_opacity.valueChanged.connect", "self.h12_weight.valueChanged.connect", "self.h12_cover_check.toggled.connect"):
    if tok not in src: fail('H12 compatibility owner changed: '+tok)

note=root/'PREVIEW_STAGE_APPEARANCE_INSPECTOR_H74_NOTE_20260905.md'
if not note.is_file(): fail('missing H74 note')
text=note.read_text(encoding='utf-8')
for tok in ('presentation-only','18 characters','24 ms','no config keys','QPainter'):
    if tok not in text: fail('H74 note incomplete: '+tok)

print('PREVIEW STAGE + APPEARANCE INSPECTOR H74 REPLAY: PASS')
print(' - Appearance has a live vector style stage plus weight/opacity/cover-follow inspector using existing H12 config owners')
print(' - preset CRUD is collapsed into a discoverable overflow menu without replacing existing methods')
print(' - Motion has a bounded exit-only replay preview reading H70/H71 profiles but never owning desktop timing/lifecycle')
print(' - H74 is presentation-only, timer-bounded, dependency-free and leaves player/provider/seek/runtime renderer ownership unchanged')
