"""H91 draggable workspace / media-first hero / shared cover replay."""
import ast, sys
from pathlib import Path
sys.dont_write_bytecode=True
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_DRAGGABLE_WORKSPACE_MEDIA_FIRST_SHARED_COVER_H91_REPLAY.py <root>')
root=Path(sys.argv[1]).resolve(); main=next(root.glob('LimbusLyric_*.py')); src=main.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def node(name):
    n=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.name==name),None)
    if n is None: raise SystemExit('H91 missing '+name)
    return n
def text(name): return ast.get_source_segment(src,node(name)) or ''
ck('H91 build tag','+ DRAGGABLE WORKSPACE + MEDIA-FIRST HERO + SHARED COVER H91' in src)
start=src.index('# H91 draggable workspace'); end=src.index('# H92 navigation-button drag gesture arbitration',start); block=src[start:end]
for bad in ('MediaSessionSync.','_merge_uia_position','qq-seek-session','LyricSearchEngine.search_','FadingLine.'):
    ck('presentation boundary excludes '+bad,bad not in block)
ck('nav background installs vertical splitter','class H91WorkspaceSplitter' in block and 'nav.installEventFilter(self)' in block and 'Qt.SizeVerCursor' in block)
ck('splitter preserves child nav button clicks','if obj is not self.nav: return False' in text('H91WorkspaceSplitter'))
ck('up-down drag changes only hero height','self.start_h + (self._global_y(event) - self.start_y)' in text('H91WorkspaceSplitter') and '_h91_apply_hero_height' in text('H91WorkspaceSplitter'))
ck('double click restores default hero','MouseButtonDblClick' in text('H91WorkspaceSplitter') and 'H91_HERO_DEFAULT_H' in text('H91WorkspaceSplitter'))
ck('hero height persists',"settings['h91_hero_height']" in text('_h91_save_all_config') and "settings.get('h91_hero_height'" in text('_h91_control_init'))
ck('hero has bounded compact range','H91_HERO_MIN_H = 96' in block and 'H91_HERO_MAX_H = 252' in block)
ck('compact hero keeps record route','ambient.setVisible(int(panel.width()) >= 500)' in text('_h91_apply_hero_height'))
ck('record scales with hero height','r=max(32.0,min(66.0,(rect.height()-18.0)*0.46))' in text('_h91_ambient_paint'))
ck('media identity drives front label','_h91_source_affine_media(panel)' in text('_h91_refresh_frontend_status') and 'panel.front_track_label.setText' in text('_h91_refresh_frontend_status'))
ck('media-first shell does not rewrite loaded lyric identity','_loaded_song =' not in text('_h91_refresh_frontend_status') and '_loaded_artist =' not in text('_h91_refresh_frontend_status'))
ck('process affinity checked for media title','_source_matches_process_hint' in text('_h91_source_affine_media'))
ck('record request follows media duration','state.get(\'duration_ms\')' in text('_h91_refresh_frontend_status'))
ck('shared pipeline replaces both artwork and cover tick',"globals()['_h87_request_art']=_h91_request_art" in block and "globals()['_h16_cover_tick']=_h91_cover_tick" in block)
ck('shared artwork feeds cover colour cache','_h16_cover_color_from_image' in text('_h91_share_art_color') and '_h16_cover_cache' in text('_h91_share_art_color'))
ck('shared colour persists through H85 cache','_h85_persist_new_cover_colors' in text('_h91_share_art_color'))
ck('colour-only cache still requests artwork','_h91_request_art(panel,song,artist' in text('_h91_cover_tick'))
ck('QQ and NetEase stay fallback providers','_h91_fetch_qq_art' in text('_h91_request_art') and '_h91_fetch_netease_art' in text('_h91_request_art'))
ck('artwork fetch stays daemonized',"daemon=True" in text('_h91_request_art'))
ck('old record clears after bounded grace','H91_ART_CLEAR_GRACE_MS = 360' in block and '_h91_clear_stale_record' in text('_h91_request_art'))
ck('negative art retry is bounded','H91_ART_NEGATIVE_RETRY_SEC = 28.0' in block and '_h88_art_negative' in text('_h91_request_art'))
ck('H91 note present',(root/'DRAGGABLE_WORKSPACE_MEDIA_FIRST_SHARED_COVER_H91_NOTE_20260906.md').is_file())

# Pure identity helpers: bracket-heavy titles such as the field-log 少女A case must expose
# a canonical title and producer/vocal aliases, while duration scoring prefers the real edit.
names=['_h91_song_variants','_h91_bracket_aliases','_h91_artist_variants','_h91_norm','_h91_duration_score','_h91_artist_match','_h91_choose_qq_row','_h91_choose_netease_row']
body=[node(n) for n in names]
ns={'re':__import__('re'),'H91_QQ_DURATION_TOL_MIN':3500,
    '_artist_alias_match':lambda a,b:(str(a).casefold() in str(b).casefold() or str(b).casefold() in str(a).casefold(),''),
    '_artist_text':lambda row:', '.join(str(x.get('name') or '') for x in row.get('singer',[]) if isinstance(x,dict)),
    '_h16_cover_pic_url':lambda row:str(((row.get('album') or row.get('al') or {}) if isinstance(row,dict) else {}).get('picUrl') or '')}
exec(compile(ast.Module(body=body,type_ignores=[]),str(main),'exec'),ns)
variants=ns['_h91_song_variants']('【鏡音リン】少女A【椎名もた】')
ck('bracket-heavy title exposes canonical 少女A','少女A' in variants)
aliases=ns['_h91_artist_variants']('【鏡音リン】少女A【椎名もた】','ぽわぽわP/鏡音リン')
ck('title brackets enrich artist aliases','椎名もた' in aliases and '鏡音リン' in aliases and 'ぽわぽわP' in aliases)
rows=[
 {'songname':'少女A','singer':[{'name':'Other'}],'interval':203,'albummid':'wrong'},
 {'songname':'少女A','singer':[{'name':'椎名もた'}],'interval':242,'albummid':'right'},
]
hit=ns['_h91_choose_qq_row'](rows,'少女A','椎名もた',242000)
ck('QQ artwork identity prefers matching 242s edit',isinstance(hit,dict) and hit.get('albummid')=='right')
ck('duration score rejects far edit',ns['_h91_duration_score'](203000,242000)<0 and ns['_h91_duration_score'](242000,242000)>0)
print(f'H91 DRAGGABLE WORKSPACE / MEDIA-FIRST HERO / SHARED COVER: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
