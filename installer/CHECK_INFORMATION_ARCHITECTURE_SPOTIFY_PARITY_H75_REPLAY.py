from pathlib import Path
import ast, sys, textwrap
if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_INFORMATION_ARCHITECTURE_SPOTIFY_PARITY_H75_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines(); root=path.parent

def fail(msg): raise SystemExit('H75 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name: return node
    fail('function not found: '+name)
def method(clsname,name):
    for node in tree.body:
        if isinstance(node,ast.ClassDef) and node.name==clsname:
            for child in node.body:
                if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)) and child.name==name: return child
    fail(f'method not found: {clsname}.{name}')
def source_of(node): return textwrap.dedent('\n'.join(lines[node.lineno-1:node.end_lineno]))

def msrc(clsname,name): return source_of(method(clsname,name))
def fsrc(name): return source_of(fn(name))

need('+ INFORMATION ARCHITECTURE + SPOTIFY PARITY H75','build tag')
need('# H75 information architecture + Spotify parity','source marker')
need("if '_h75_activate_ui' in globals():",'activation')
if not (src.rindex("if '_h74_activate_ui' in globals():") < src.rindex("if '_h75_activate_ui' in globals():")):
    fail('H75 must activate after H74')
for name in ('_h75_card_for_widget','_h75_find_card_by_title','_h75_bind_spin_proxy','_h75_bind_combo_proxy','_h75_apply_live_sync_offset','_h75_make_application_card','_h75_make_sync_output_card','_h75_make_update_card','_h75_global_filter','_h75_filter_settings_cards','_h75_on_settings_page_changed','_h75_control_init','_h75_activate_ui'):
    fn(name)

block=src[src.index('# H75 information architecture + Spotify parity'):]
if '# H76 editorial polish + wipe refinement + blur recovery' in block:
    block=block[:block.index('# H76 editorial polish + wipe refinement + blur recovery')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync.', 'LyricSearchEngine.', '_commit_seek', '_on_seek', 'threading.Thread(', 'requests.', 'QImage(', 'QPixmap.fromImage(', '_discard_fading_item(', 'fading_lines.append(', 'history_lines.append('):
    if bad in block: fail('H75 crossed UI/config boundary: '+bad)

init=msrc('ControlPanel','__init__')
for tok in ('self.diy_scope_combo.addItem("Spotify", "spotify")','QQ音乐 / 网易云 / 酷狗 / Spotify 四家独立'):
    if tok not in init: fail('Spotify DIY UI parity missing '+tok)

scope=msrc('ControlPanel','_song_style_scope_key')
ns={}; exec('class H:\n'+textwrap.indent(scope,'    '),ns); H=ns['H']
for value,want in (('QQ音乐','qq'),('cloudmusic.exe','netease'),('kgmusic.exe','kugou'),('Spotify','spotify'),('spotify.exe','spotify')):
    if H._song_style_scope_key(value)!=want: fail(f'scope resolver {value} -> {H._song_style_scope_key(value)} not {want}')

row_mode=msrc('ControlPanel','_diy_row_mode'); apply=msrc('ControlPanel','_apply_song_style_for_track')
ns={}; exec('class A:\n'+textwrap.indent(row_mode,'    ')+'\n'+textwrap.indent(apply,'    '),ns); a=ns['A']()
a._song_style_scope_key=lambda p:H._song_style_scope_key(p); a._song_style_identity_for_track=lambda s,ar='':'s|a'; a._ensure_random_style_for_track=lambda s,ar:{'random':1}
a.song_styles={'s|a':{'mode':'per_player','rules':{'qq':{'v':'q'},'netease':{'v':'n'},'kugou':{'v':'k'},'spotify':{'v':'s'},'all':{'v':'all'}}}}
if a._apply_song_style_for_track('s','a','Spotify').get('v')!='s': fail('Spotify per-song rule is not runtime authoritative')
a.song_styles['s|a']['mode']='all'
if a._apply_song_style_for_track('s','a','Spotify').get('v')!='all': fail('ALL mode no longer covers Spotify')

load=fsrc('load_all_config')
for tok in ("for scope in ('all', 'qq', 'netease', 'kugou', 'spotify')", "('qq', 'netease', 'kugou', 'spotify')"):
    if tok not in load: fail('config normalizer would drop Spotify DIY data: '+tok)

save=fsrc('save_all_config')
if "'spotify_sync_offset'" not in save or "_h75_spotify_sync_offset_ms" not in save:
    fail('Spotify offset is not persisted safely before/after H75 widget creation')
offset=fsrc('_h75_apply_live_sync_offset')
if "if 'SPOTIFY' in upper_name" not in offset or 'spotify_sync_offset_spin' not in offset:
    fail('Spotify still falls through to NetEase offset')

search=fsrc('_h75_global_filter')
for tok in ('range(panel.main_tabs.count())','matching_pages','panel.main_tabs.setCurrentIndex(matching_pages[0])',"'h75SearchIgnore'",'total_visible'):
    if tok not in search: fail('global settings search contract missing '+tok)
base_offset=msrc('ControlPanel','_apply_live_sync_offset')
if "'SPOTIFY'" in base_offset: fail('mature live-offset method was modified instead of using H75 wrapper')
activate=fsrc('_h75_activate_ui')
if "ControlPanel._apply_live_sync_offset = _h75_apply_live_sync_offset" not in activate: fail('H75 Spotify offset wrapper is not installed')
page_change=fsrc('_h75_on_settings_page_changed')
if '.clear()' in page_change: fail('global query is still cleared on page navigation')

panel=fsrc('_h75_control_init')
for tok in ("_h75_find_card_by_title(motion_layout, '同步')", "QLabel('同步与输出')", "QLabel('应用界面')", "QLabel('更新')", "setPlaceholderText('搜索全部设置…')", "h12_owner.setProperty('h75SearchIgnore', True)"):
    if tok not in src: fail('semantic settings re-home missing '+tok)
if "panel._apply_live_sync_offset()" not in panel: fail('initial Spotify offset is not applied after widget creation')

note=root/'INFORMATION_ARCHITECTURE_SPOTIFY_PARITY_H75_NOTE_20260905.md'
if not note.is_file(): fail('missing H75 note')
text=note.read_text(encoding='utf-8')
for tok in ('global search','Spotify','同步与输出','H12','no playback/seek/provider authority'):
    if tok not in text: fail('H75 note incomplete: '+tok)

print('INFORMATION ARCHITECTURE + SPOTIFY PARITY H75 REPLAY: PASS')
print(' - Motion no longer presents player sync controls; Settings owns semantic Sync & Output proxies')
print(' - settings search spans all five pages and survives navigation')
print(' - Spotify has independent display offset plus persistent/runtime per-song DIY scope')
print(' - H12 compatibility owners remain behind semantic Application/Update surfaces')
print(' - H75 does not take player/provider/seek/desktop-exit lifecycle ownership')
