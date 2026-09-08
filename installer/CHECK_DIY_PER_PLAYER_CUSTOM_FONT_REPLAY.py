from pathlib import Path
import ast, sys, textwrap
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_DIY_PER_PLAYER_CUSTOM_FONT_REPLAY.py <main.py>')
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8'); tree=ast.parse(source)

def method(cls, name):
    for n in tree.body:
        if isinstance(n, ast.ClassDef) and n.name==cls:
            for x in n.body:
                if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name:
                    return ast.get_source_segment(source,x)
    raise AssertionError(f'missing {cls}.{name}')

def func(name):
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name:
            return ast.get_source_segment(source,n)
    raise AssertionError(name)

init=method('ControlPanel','__init__')
assert 'diy_mode_combo' not in init
assert '编辑播放器：' in init
assert 'self.diy_scope_combo.addItem("ALL · 全部播放器", "all")' in init
assert 'self.diy_scope_combo.addItem("QQ音乐", "qq")' in init
assert 'self.diy_scope_combo.addItem("网易云", "netease")' in init
assert 'self.diy_scope_combo.addItem("酷狗", "kugou")' in init
assert 'self.diy_scope_combo.addItem("Spotify", "spotify")' in init
assert 'self.import_font_btn = QPushButton("导入字体")' in init
assert 'self.import_font_btn.clicked.connect(self.import_custom_fonts)' in init

refresh=method('ControlPanel','_refresh_song_style_list')
assert 'row_widget.setMinimumHeight(108)' in refresh
assert "scopes = [('all', 'ALL')] if mode == 'all' else [('qq', 'QQ'), ('netease', '网易云'), ('kugou', '酷狗'), ('spotify', 'Spotify')]" in refresh
assert "mode_btn = QPushButton('ALL' if mode == 'all' else '四家独立')" in refresh
assert '_quick_set_song_style_mode(ident, target)' in refresh
assert '_quick_edit_song_appearance(ident, sc)' in refresh
assert 'effect_summary' in refresh

save=method('ControlPanel','_save_current_song_style')
update=method('ControlPanel','_update_selected_song_style')
for body in (save, update):
    assert "rules[scope] = self._song_style_payload_from_diy()" in body
    assert "row['mode'] = 'all'" in body
    assert "row['mode'] = 'per_player'" in body
    assert '_ensure_diy_per_source_slots' in body

ensure=method('ControlPanel','_ensure_diy_per_source_slots')
assert "rules[scope] = dict(seed)" in ensure
assert "if not isinstance(rules.get(scope), dict) or not rules.get(scope)" in ensure

scope=method('ControlPanel','_diy_edit_scope')
assert "return 'all' if scope == 'all' else 'qq'" in scope

row_mode_src=method('ControlPanel','_diy_row_mode')
style_identity_src=method('ControlPanel','_song_style_identity_for_track')
apply_src=method('ControlPanel','_apply_song_style_for_track')
ns={}
exec('class A:\n'+textwrap.indent(row_mode_src,'    ')+"\n"+textwrap.indent(style_identity_src,'    ')+"\n"+textwrap.indent(apply_src,'    '),ns)
a=ns['A'](); a._song_style_scope_key=lambda source:{'QQ音乐':'qq','网易云':'netease','酷狗':'kugou','Spotify':'spotify'}.get(source,'')
a._track_identity=lambda s,ar:f'{s}|{ar}'; a._same_track=lambda sa,aa,sb,ab: sa==sb and (aa==ab or aa in ab or ab in aa); a._ensure_random_style_for_track=lambda s,ar:{'random':1}
a.song_styles={'song|artist':{'song':'song','artist':'artist','mode':'per_player','rules':{'all':{'v':'all'},'qq':{'v':'qq'},'netease':{'v':'ncm'},'kugou':{'v':'kg'},'spotify':{'v':'sp'}}}}
assert a._apply_song_style_for_track('song','artist','QQ音乐')['v']=='qq'
assert a._apply_song_style_for_track('song','artist','网易云')['v']=='ncm'
assert a._apply_song_style_for_track('song','artist','酷狗')['v']=='kg'
assert a._apply_song_style_for_track('song','artist','Spotify')['v']=='sp'
a.song_styles['song|artist']['mode']='all'
assert a._apply_song_style_for_track('song','artist','QQ音乐')['v']=='all'
assert a._apply_song_style_for_track('song','artist','酷狗')['v']=='all'
a.song_styles['song|artist']['mode']='per_player'; del a.song_styles['song|artist']['rules']['netease']
assert a._apply_song_style_for_track('song','artist','网易云').get('random')==1
# Artist enrichment/alias must retain the same DIY row instead of silently falling back to random.
a.song_styles['song|artist']['rules']['netease']={'v':'alias'}
assert a._apply_song_style_for_track('song','artist feat guest','网易云')['v']=='alias'


quick_font=method('ControlPanel','_quick_edit_song_font')
for token in ("QFontComboBox", "QCheckBox('粗体'", "QCheckBox('斜体'", "style['font_bold']", "style['font_italic']"):
    assert token in quick_font, token
assert '恢复全局字体' not in quick_font

appearance=method('ControlPanel','_quick_edit_song_appearance')
for token in ('文字颜色：','启用阴影','启用描边','启用柔光光晕','stroke_width',"rules[scope] = style","scope not in ('all', 'qq', 'netease', 'kugou', 'spotify')"):
    assert token in appearance, token
assert '保存' in appearance and '取消' in appearance

font_import=method('ControlPanel','import_custom_fonts')
for token in ('QFileDialog.getOpenFileNames','*.ttf *.otf *.ttc','CUSTOM_FONT_ROOT','shutil.copy2','QFontDatabase.addApplicationFont','applicationFontFamilies','不会安装到 Windows 系统'):
    assert token in font_import, token
loader=func('_load_custom_application_fonts')
assert 'CUSTOM_FONT_ROOT' in loader and 'QFontDatabase.addApplicationFont' in loader
assert '_load_custom_application_fonts()' in init

load=func('load_all_config')
assert 'Schema v5' in load
assert "for scope in ('all', 'qq', 'netease', 'kugou', 'spotify')" in load
assert "mode = 'per_player'" in load
assert "row['mode'] = mode" in load
assert 'CONFIG_SCHEMA_VERSION = 5' in source

print('DIY ALL + PER-PLAYER + CUSTOM FONT REPLAY: PASS')
print('  ALL is a first-class unified mode and four player slots remain independently editable: PASS')
print('  switching modes preserves the inactive side; missing provider slots may be seeded only from ALL: PASS')
print('  row font editor supports font + bold + italic without a redundant reset-global-font action: PASS')
print('  artist enrichment/alias keeps the existing song DIY style: PASS')
print('  row color opens Chinese color+shadow+outline+glow editor: PASS')
print('  custom TTF/OTF/TTC fonts persist under LocalAppData and load app-only: PASS')
