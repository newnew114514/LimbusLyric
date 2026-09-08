"""H90 responsive shell / record restore / density fix replay."""
import ast, sys, types
from pathlib import Path
sys.dont_write_bytecode=True
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_RESPONSIVE_SHELL_RECORD_RESTORE_DENSITY_FIX_H90_REPLAY.py <root>')
root=Path(sys.argv[1]).resolve(); main=next(root.glob('LimbusLyric_*.py')); src=main.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def fn(name):
    n=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
    if n is None: raise SystemExit('H90 missing '+name)
    return ast.get_source_segment(src,n) or '',n
ck('H90 build tag','+ RESPONSIVE SHELL + RECORD RESTORE + DENSITY FIX H90' in src)
start=src.index('# H90 responsive shell + record restore + density fix'); end=src.index('# H91 draggable workspace + media-first hero + shared cover pipeline',start); block=src[start:end]
for bad in ('MediaSessionSync.','_merge_uia_position','qq-seek-session','LyricSearchEngine.search_','FadingLine.'):
    ck('presentation boundary excludes '+bad,bad not in block)
ck('compact minimum geometry','H90_MIN_PANEL_WIDTH = 520' in block and 'H90_MIN_PANEL_HEIGHT = 360' in block and 'panel.setMinimumSize(int(H90_MIN_PANEL_WIDTH), int(H90_MIN_PANEL_HEIGHT))' in block)
ck('settings shell can shrink','QSizePolicy.Expanding, QSizePolicy.Ignored' in block and 'tabs.setMinimumHeight(82)' in block)
ck('scale wrapper reapplies shell density',"globals()['_h12_apply_scale'] = _h90_apply_scale" in block and '_h90_relax_shell(panel)' in fn('_h90_apply_scale')[0])
ck('section chip rail fully retired','_h90_remove_section_rail(panel)' in block and 'panel.h88_section_rail = None' in block and "globals()['_h89_rebuild_section_rail'] = _h90_no_section_rail" in block)
ck('record restored below old 800 threshold','H90_RECORD_VISIBLE_MIN_WIDTH = 500' in block and 'ambient.setVisible(width >= int(H90_RECORD_VISIBLE_MIN_WIDTH))' in block)
ck('hero reserves compact record space','right = 150 if width >= int(H90_RECORD_VISIBLE_MIN_WIDTH) else 22' in block)
title,_=fn('_h90_title_press')
ck('titlebar no manual native resize transaction','PostMessageW' not in title and 'SendMessageW' not in title and 'startSystemResize' not in title)
ck('top strip cannot become window drag','event.ignore()' in title and 'bar._drag_offset = None' in title)
ck('old resize helpers runtime-disabled',"globals()['_h86_try_top_system_resize'] = lambda *_a, **_k: False" in block and "globals()['_h89_try_top_system_resize'] = lambda *_a, **_k: False" in block)
rescue,rnode=fn('_h90_rescue_geometry')
ck('geometry rescue waits for mouse release','QApplication.mouseButtons() & Qt.LeftButton' in rescue)
ck('geometry rescue preserves width','panel.resize(panel.width(), h)' in rescue and 'setMaximumWidth' not in rescue)
ck('geometry rescue only after settle','H90_GEOMETRY_SETTLE_MS = 360' in block and '_h90_schedule_geometry_guard(panel)' in fn('_h90_resize')[0])
ck('H90 note present',(root/'RESPONSIVE_SHELL_RECORD_RESTORE_DENSITY_FIX_H90_NOTE_20260906.md').is_file())

# Pure geometry replay: compact minimum allows 360, oversize 1200 is rescued to 900,
# while an active mouse gesture is never interrupted.
class Rect:
    def __init__(self,x=0,y=0,w=1920,h=900): self._x=x; self._y=y; self._w=w; self._h=h
    def height(self): return self._h
    def top(self): return self._y
    def bottom(self): return self._y+self._h-1
class Screen:
    def availableGeometry(self): return Rect()
class Geo:
    def __init__(self,x,y,w,h): self._x=x; self._y=y; self._w=w; self._h=h
    def y(self): return self._y
    def height(self): return self._h
class QtStub: LeftButton=1
class App:
    held=0
    @staticmethod
    def mouseButtons(): return App.held
    @staticmethod
    def primaryScreen(): return Screen()
class P:
    def __init__(self,h=1200,y=-80): self.xv=12; self.yv=y; self.w=740; self.h=h
    def isMaximized(self): return False
    def geometry(self): return Geo(self.xv,self.yv,self.w,self.h)
    def width(self): return self.w
    def x(self): return self.xv
    def y(self): return self.yv
    def resize(self,w,h): self.w=w; self.h=h
    def move(self,x,y): self.xv=x; self.yv=y
ns={'QApplication':App,'Qt':QtStub,'_h89_screen_for_panel':lambda p:Screen(),'_h90_schedule_geometry_guard':lambda *a,**k:None,'H90_MIN_PANEL_HEIGHT':360}
exec(compile(ast.Module(body=[rnode],type_ignores=[]),str(main),'exec'),ns)
p=P(); ck('oversize replay clamps without width growth',ns['_h90_rescue_geometry'](p) and p.h==900 and p.w==740 and p.yv==0)
p=P(); App.held=1; ck('active resize replay is untouched',not ns['_h90_rescue_geometry'](p) and p.h==1200 and p.yv==-80); App.held=0
p=P(h=500,y=30); ck('normal in-bounds geometry remains stable',not ns['_h90_rescue_geometry'](p) and p.h==500 and p.yv==30)
print(f'H90 RESPONSIVE SHELL / RECORD RESTORE / DENSITY FIX: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
