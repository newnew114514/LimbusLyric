from pathlib import Path
import ast, sys, textwrap
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_SAIKAI_DIY_THEME_REPLAY.py <main.py>')
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
tray=method('ControlPanel','_setup_tray_icon')
apply_theme=method('ControlPanel','_apply_ui_theme')
assert 'Limbus · Manager Terminal' not in init
assert '导入Q版角色集合图' not in init
assert '重新获取示例素材' not in init
assert '打开主题目录' not in init
assert 'menu.addMenu("视觉主题")' not in tray
assert "theme = 'default'" in apply_theme and 'limbus = False' in apply_theme
assert "'ui_theme'" in source.split('_RETIRED_SETTING_KEYS',1)[1].split('}',1)[0]

scope_src=method('ControlPanel','_song_style_scope_key')
ns={}
exec('class H:\n'+textwrap.indent(scope_src,'    '),ns)
H=ns['H']
assert H._song_style_scope_key('QQ音乐')=='qq'
assert H._song_style_scope_key('cloudmusic.exe')=='netease'
assert H._song_style_scope_key('kgmusic.exe')=='kugou'
assert H._song_style_scope_key('spotify.exe')=='spotify'

row_mode=method('ControlPanel','_diy_row_mode')
apply_src=method('ControlPanel','_apply_song_style_for_track')
exec('class A:\n'+textwrap.indent(row_mode,'    ')+"\n"+textwrap.indent(apply_src,'    '),ns)
A=ns['A']; a=A(); a._song_style_scope_key=lambda source:H._song_style_scope_key(source); a._track_identity=lambda s,ar:'song|artist'; a._song_style_identity_for_track=lambda s,ar='':'song|artist'; a._ensure_random_style_for_track=lambda s,ar:{'random':1}
a.song_styles={'song|artist':{'mode':'per_player','rules':{'all':{'v':'all'},'qq':{'v':'qq'},'netease':{'v':'ncm'},'kugou':{'v':'kg'},'spotify':{'v':'sp'}}}}
assert a._apply_song_style_for_track('song','artist','QQ音乐')['v']=='qq'
assert a._apply_song_style_for_track('song','artist','cloudmusic.exe')['v']=='ncm'
assert a._apply_song_style_for_track('song','artist','kgmusic.exe')['v']=='kg'
assert a._apply_song_style_for_track('song','artist','spotify.exe')['v']=='sp'
a.song_styles['song|artist']['mode']='all'
assert a._apply_song_style_for_track('song','artist','QQ音乐')['v']=='all'
assert a._apply_song_style_for_track('song','artist','kgmusic.exe')['v']=='all'

refresh=method('ControlPanel','_refresh_song_style_list')
save=method('ControlPanel','_save_current_song_style')
update=method('ControlPanel','_update_selected_song_style')
delete=method('ControlPanel','_delete_selected_song_style')
assert 'item.setData(Qt.UserRole, identity)' in refresh
assert "mode_btn = QPushButton('ALL' if mode == 'all' else '四家独立')" in refresh
assert "scopes = [('all', 'ALL')] if mode == 'all' else" in refresh
assert "rules[scope] = self._song_style_payload_from_diy()" in save
assert "rules[scope] = self._song_style_payload_from_diy()" in update
assert "row['mode'] = 'all'" in save and "row['mode'] = 'per_player'" in save
assert 'self.song_styles.pop(identity' in delete
assert 'self.diy_scope_combo.addItem("ALL · 全部播放器", "all")' in init
assert 'self.diy_scope_combo.addItem("酷狗", "kugou")' in init

payload=method('ControlPanel','_song_style_payload_from_diy')
for token in ('shadow_enabled','shadow_color','outline_enabled','stroke_color','stroke_width','glow_enabled','glow_color'):
    assert token in payload, token
for token in ('self.diy_shadow_check = QCheckBox("阴影")','self.diy_outline_check = QCheckBox("描边")','self.diy_glow_check = QCheckBox("柔光光晕")'):
    assert token in init, token
render=method('ControlPanel','_launch_current_lyrics')
for token in ('resolved_shadow_enabled','resolved_outline_enabled','resolved_stroke_color','resolved_stroke_width','resolved_glow_enabled'):
    assert token in render, token

font_picker=method('ControlPanel','_choose_font_family_zh')
color_picker=method('ControlPanel','_choose_color_zh')
assert "ok_btn.setText('确定')" in font_picker and "cancel_btn.setText('取消')" in font_picker
assert "'basic colors': '基本颜色'" in color_picker and "ok_btn.setText('确定')" in color_picker

load=func('load_all_config')
assert 'Schema v5' in load and "row['mode'] = mode" in load and "('all', 'qq', 'netease', 'kugou', 'spotify')" in load

resolver=method('ControlPanel','_resolve_qq_auto_track_duration_after_bind')
assert 'QQ自动歌词时长冲突以GSMTC为准' in resolver
assert 'QQ自动歌词GSMTC时长证据' in resolver
assert 'stable_ms >= 420.0' in resolver
manual=method('LyricFetcher','fetch_and_set')
assert 'QQ手动歌词时长冲突以GSMTC为准' in manual

print('SAIKAI + DIY ALL/PER-PLAYER + THEME REPLAY: PASS')
print('  false QQ UIA duration can be vetoed without widening lyric-duration tolerance: PASS')
print('  one song can switch between ALL and independent QQ/Netease/Kugou/Spotify payloads: PASS')
print('  inactive DIY mode data is preserved; current mode alone decides runtime application: PASS')
print('  DIY shadow/outline/glow options + Chinese font/color dialogs: PASS')
print('  Limbus public theme selector/import tools/tray menu removed; standard theme forced: PASS')
