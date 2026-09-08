"""H88 inspector workspace / cover fallback / smooth nav replay."""
import ast, sys, types
from pathlib import Path
sys.dont_write_bytecode=True
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_INSPECTOR_WORKSPACE_COVER_FALLBACK_SMOOTH_NAV_H88_REPLAY.py <root>')
root=Path(sys.argv[1]).resolve(); main=next(root.glob('LimbusLyric_*.py')); src=main.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def fn(name):
    node=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
    if node is None: raise SystemExit('H88 missing function '+name)
    return ast.get_source_segment(src,node) or '',node
ck('H88 build tag','+ INSPECTOR WORKSPACE + COVER FALLBACK + SMOOTH NAV H88' in src)
start=src.index('# H88 inspector workspace + cover fallback + smooth navigation')
end=src.index('# H89 collapsible preview + resize stability + micro interactions',start); block=src[start:end]
for bad in ('MediaSessionSync.','_merge_uia_position','qq-seek-session','LyricSearchEngine.search_','FadingLine.'):
    ck('presentation boundary excludes '+bad,bad not in block)
ck('single-surface transition class','class H88PageTransitionOverlay' in block and 'self._old = QPixmap(old_pix)' in block and 'self._new = QPixmap' not in block)
trans,_=fn('_h88_on_page_changed')
ck('page change does not capture new snapshot','_h87_capture_page_region' not in trans and 'H88PageTransitionOverlay' in trans)
ck('active H87 transition owner replaced',"globals()['H87PageTransitionOverlay'] = H88PageTransitionOverlay" in block and "globals()['_h87_on_page_changed'] = _h88_on_page_changed" in block)
ck('refresh-aware animation cadence','_h79_ui_frame_interval(panel)' in block and 'H88_PAGE_TRANSITION_MS = 184' in block)
ck('preview compact by default','H88_PREVIEW_DEFAULT_EXPANDED = False' in block and 'H88_PREVIEW_COMPACT_STAGE_H = 96' in block)
ck('preview expand control exists',"setText('收起预览' if expanded else '展开预览')" in block and "settings['h88_preview_expanded']" in block)
ck('section rail subtitle motion only','visible = idx in (1, 2)' in block and "setObjectName('h88SectionChip')" in block)
ck('section jump animates scroll','QPropertyAnimation(bar' in block and 'H88_SECTION_SCROLL_MS = 210' in block)
ck('settings surfaces softened','QFrame#settingsCard { background:rgba(18,29,24,168)' in block and 'QFrame#settingsCard { background:rgba(16,16,19,170)' in block)
ck('cover fallback includes QQ and NetEase','def _h88_fetch_qq_art' in block and 'def _h88_fetch_netease_art' in block and "order = ('qq','netease') if process == 'qqmusic' else ('netease','qq')" in block)
ck('QQ album artwork endpoint used','T002R500x500M000' in block and 'albummid' in block)
ck('translated title suffix stripped',"re.sub(r'\\s*[\\(（][^()（）]{1,48}[\\)）]\\s*$'" in block)
ck('cover failure backoff','H88_COVER_NEGATIVE_RETRY_SEC = 24.0' in block and "negative[str(key)] = time.monotonic()" in block)
ck('stale prior cover retires', 'H88_COVER_CLEAR_GRACE_MS = 420' in block and 'ambient._h87_cover = QPixmap()' in block)
ck('cover work stays daemonized',"threading.Thread(target=work, name='LimbusLyric-H88HeroCover', daemon=True).start()" in block)
ck('H87 cache is reused','_h87_cached_art_path(key)' in block and '_h87_art_file_for_key(key)' in block)
ck('H88 note present',(root/'INSPECTOR_WORKSPACE_COVER_FALLBACK_SMOOTH_NAV_H88_NOTE_20260906.md').is_file())

# Small behavior replay for normalization and dimensions.
_,sv=fn('_h88_song_variants'); _,av=fn('_h88_artist_variants'); _,pd=fn('_h88_preview_dimensions')
ns={'str':str,'re':__import__('re'),'H88_PREVIEW_EXPANDED_STAGE_H':174,'H88_PREVIEW_EXPANDED_HOST_H':238,'H88_PREVIEW_COMPACT_STAGE_H':96,'H88_PREVIEW_COMPACT_HOST_H':160}
mod=ast.Module(body=[sv,av,pd],type_ignores=[]); exec(compile(mod,str(main),'exec'),ns)
ck('song alias normalization behavior',ns['_h88_song_variants']('My Way (风可以越过荆棘)')==['My Way (风可以越过荆棘)','My Way'])
ck('artist primary fallback behavior',ns['_h88_artist_variants']('TypeD/Veysigz')==['TypeD/Veysigz','TypeD'])
ck('preview dimensions behavior',ns['_h88_preview_dimensions'](False)==(96,160) and ns['_h88_preview_dimensions'](True)==(174,238))
print(f'H88 INSPECTOR WORKSPACE / COVER FALLBACK / SMOOTH NAV: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
