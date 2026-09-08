"""H89 collapsible preview / resize stability / micro interactions replay."""
import ast, sys, types
from pathlib import Path
sys.dont_write_bytecode=True
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_COLLAPSIBLE_PREVIEW_RESIZE_STABILITY_MICRO_INTERACTIONS_H89_REPLAY.py <root>')
root=Path(sys.argv[1]).resolve(); main=next(root.glob('LimbusLyric_*.py')); src=main.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def fn(name):
    n=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
    if n is None: raise SystemExit('H89 missing '+name)
    return ast.get_source_segment(src,n) or '',n
ck('H89 build tag','+ COLLAPSIBLE PREVIEW + RESIZE STABILITY + MICRO INTERACTIONS H89' in src)
start=src.index('# H89 collapsible preview + resize stability + micro interactions'); end=src.index('# H90 responsive shell + record restore + density fix',start); block=src[start:end]
for bad in ('MediaSessionSync.','_merge_uia_position','qq-seek-session','LyricSearchEngine.search_','FadingLine.'):
    ck('presentation boundary excludes '+bad,bad not in block)
ck('snapshot page compositing retired','panel.grab(' not in block and '_h87_capture_page_region(' not in block and 'QPixmap(old_pix)' not in block)
ck('paint-only page veil exists','class H89PageVeil' in block and 'H89_PAGE_VEIL_MS = 138' in block)
ck('old snapshot callbacks neutralized',"globals()['_h87_prime_page_transition']=_h89_prime_page_transition" in block and "globals()['_h87_refresh_page_snapshot']=_h89_refresh_page_snapshot" in block)
ck('preview has one compact open size','H89_PREVIEW_STAGE_H = 92' in block and 'H89_PREVIEW_OPEN_HOST_H = 154' in block and 'H89_PREVIEW_CLOSED_HOST_H = 48' in block)
ck('preview rail says only preview',"btn.setText('预览')" in block and "setObjectName('h89PreviewRailButton')" in block)
ck('legacy H88 size buttons retire',"getattr(panel, '_h88_preview_buttons'" in block and 'old.hide(); old.deleteLater()' in block)
ck('preview disclosure animates','QPropertyAnimation(host, b\'maximumHeight\'' in block and 'H89_PREVIEW_ANIM_MS = 168' in block)
ck('preview state persists',"settings['h89_preview_open']" in block)
ck('section rail rehomed after header','shell_layout.indexOf(header) + 1' in block and "setObjectName('h89SectionTab')" in block)
ck('section rail has real state feedback','setCheckable(True)' in block and 'setAutoExclusive(True)' in block and "setProperty('h89Focus', True)" in block)
ck('section scroll animates','H89_SECTION_SCROLL_MS = 190' in block and "QPropertyAnimation(bar, b'value'" in block)
ck('manual lyric disclosure animates','H89_LRC_DISCLOSURE_MS = 176' in block and "QPropertyAnimation(editor,b'maximumHeight'" in block and "QPropertyAnimation(effect,b'opacity'" in block)
ck('historical H86 source not edited','# H86 frameless vertical resize recovery' in src and 'H86_TOP_RESIZE_BORDER_PX = 8' in src)
limit,_=fn('_h89_h86_limit_bridge'); rescue,rnode=fn('_h89_rescue_vertical_geometry'); top,tnode=fn('_h89_try_top_system_resize')
ck('H86 runtime rescue no longer resizes in move event','panel.resize(' not in limit and '_h89_schedule_geometry_guard(panel)' in limit)
ck('settled guard waits for mouse release','QApplication.mouseButtons() & Qt.LeftButton' in rescue)
ck('settled guard preserves width','setMaximumWidth' not in block and 'panel.resize(panel.width(),h)' in rescue)
ck('top resize has single Win32 transaction','PostMessageW' in top and 'SendMessageW' not in top and "if os.name=='nt'" in top)
ck('small-screen minimum height relaxed','H89_MIN_PANEL_HEIGHT = 460' in block and 'panel.setMinimumHeight(int(H89_MIN_PANEL_HEIGHT))' in block)
ck('H89 note present',(root/'COLLAPSIBLE_PREVIEW_RESIZE_STABILITY_MICRO_INTERACTIONS_H89_NOTE_20260906.md').is_file())

# Pure geometry replay: 1200 px high panel on 900 px work area becomes 900 high;
# width is unchanged and y is clamped. Mouse-held state postpones intervention.
class Rect:
    def __init__(self,x=0,y=0,w=1920,h=900): self._x=x; self._y=y; self._w=w; self._h=h
    def height(self): return self._h
    def top(self): return self._y
    def bottom(self): return self._y+self._h-1
class Screen:
    def availableGeometry(self): return Rect()
class Handle:
    def screen(self): return Screen()
class Geo:
    def __init__(self,x,y,w,h): self._x=x; self._y=y; self._w=w; self._h=h
    def x(self): return self._x
    def y(self): return self._y
    def height(self): return self._h
class QtStub: LeftButton=1
class App:
    held=0
    @staticmethod
    def mouseButtons(): return App.held
    @staticmethod
    def primaryScreen(): return Screen()
    @staticmethod
    def screenAt(_): return Screen()
class P:
    def __init__(self): self.xv=10; self.yv=-100; self.w=812; self.h=1200
    def isMaximized(self): return False
    def windowHandle(self): return Handle()
    def frameGeometry(self): return types.SimpleNamespace(center=lambda:None)
    def geometry(self): return Geo(self.xv,self.yv,self.w,self.h)
    def minimumHeight(self): return 460
    def width(self): return self.w
    def x(self): return self.xv
    def y(self): return self.yv
    def resize(self,w,h): self.w=w; self.h=h
    def move(self,x,y): self.xv=x; self.yv=y
ns={'QApplication':App,'Qt':QtStub,'_h89_screen_for_panel':lambda p:Screen(),'_h89_schedule_geometry_guard':lambda *a,**k:None}
exec(compile(ast.Module(body=[rnode],type_ignores=[]),str(main),'exec'),ns)
p=P(); ck('oversize replay clamps vertically',ns['_h89_rescue_vertical_geometry'](p) and p.h==900 and p.w==812 and p.yv==0)
p=P(); App.held=1; ck('active mouse ownership postpones clamp',not ns['_h89_rescue_vertical_geometry'](p) and p.h==1200 and p.yv==-100); App.held=0
print(f'H89 COLLAPSIBLE PREVIEW / RESIZE STABILITY / MICRO INTERACTIONS: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
