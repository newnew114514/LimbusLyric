"""H86 frameless top-edge vertical resize recovery replay."""
import ast, sys, types
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(sys.argv[1]).resolve(); main=next(root.glob('LimbusLyric_*.py')); src=main.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def fn(name):
    n=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    return ast.get_source_segment(src,n) or '',n
ck('H86 build tag','+ FRAMELESS VERTICAL RESIZE RECOVERY H86' in src)
start=src.index('# H86 frameless vertical resize recovery')
end=src.index('# H87 premium interaction + dynamic record + frontend palettes',start)
block=src[start:end]
for bad in ('MediaSessionSync','LyricSearchEngine','FadingLine','_merge_uia_position','seek_session','requests.'):
    ck('presentation boundary excludes '+bad,bad not in block)
press,pnode=fn('_h86_try_top_system_resize')
limit,lnode=fn('_h86_refresh_vertical_limit')
screen,snode=fn('_h86_screen_for_panel')
ck('top band precedes title move','pos.y() < 0 or pos.y() >= border' in press)
ck('Qt native resize preferred','startSystemResize' in press)
ck('Win32 native resize fallback','0x00A1' in press and 'SendMessageW' in press)
ck('top-left and top-right corners retained','Qt.TopEdge | Qt.LeftEdge' in press and 'Qt.TopEdge | Qt.RightEdge' in press)
ck('height guard uses monitor work area','availableGeometry()' in limit and 'available.height()' in limit)
ck('width is not clamped','setMaximumWidth' not in block)
ck('startup rescue scheduled','QTimer.singleShot(0' in block and 'rescue=True' in block)
ck('monitor move refresh installed','ControlPanel.moveEvent = _h86_control_move' in block)

class P:
    def __init__(self,x,y): self._x=x; self._y=y
    def x(self): return self._x
    def y(self): return self._y
class QtStub:
    LeftButton=1; TopEdge=1; LeftEdge=2; RightEdge=4
class Handle:
    def __init__(self,screen=None): self.edge=None; self._screen=screen
    def startSystemResize(self,edge): self.edge=edge; return True
    def screen(self): return self._screen
class Host:
    def __init__(self,p): self.p=p; self.h=Handle()
    def isMaximized(self): return False
    def mapFromGlobal(self,g): return self.p
    def devicePixelRatioF(self): return 1.0
    def width(self): return 800
    def windowHandle(self): return self.h
    def winId(self): return 1
class Bar:
    def __init__(self,h): self._host=h; self._drag_offset='move'
class Event:
    def __init__(self): self.accepted=False
    def button(self): return 1
    def globalPos(self): return P(0,0)
    def accept(self): self.accepted=True

ns={'Qt':QtStub,'os':types.SimpleNamespace(name='posix'),'ctypes':None,'H86_TOP_RESIZE_BORDER_PX':8}
exec(compile(ast.Module(body=[pnode],type_ignores=[]),str(main),'exec'),ns)
try_resize=ns['_h86_try_top_system_resize']
h=Host(P(400,2)); b=Bar(h); e=Event(); ck('top edge starts native resize',try_resize(b,e) and h.h.edge==QtStub.TopEdge and b._drag_offset is None)
h=Host(P(2,2)); b=Bar(h); ck('top-left starts corner resize',try_resize(b,Event()) and h.h.edge==(QtStub.TopEdge|QtStub.LeftEdge))
h=Host(P(798,2)); b=Bar(h); ck('top-right starts corner resize',try_resize(b,Event()) and h.h.edge==(QtStub.TopEdge|QtStub.RightEdge))
h=Host(P(400,20)); b=Bar(h); ck('ordinary titlebar is not stolen',not try_resize(b,Event()) and b._drag_offset=='move')

class Rect:
    def height(self): return 900
class Screen:
    def availableGeometry(self): return Rect()
class LimitHandle:
    def __init__(self): self.s=Screen()
    def screen(self): return self.s
class Panel:
    def __init__(self): self.maxh=16777215; self.h=1200; self.w=800; self.handle=LimitHandle()
    def isMaximized(self): return False
    def windowHandle(self): return self.handle
    def frameGeometry(self): return types.SimpleNamespace(center=lambda:P(0,0))
    def minimumHeight(self): return 540
    def maximumHeight(self): return self.maxh
    def setMaximumHeight(self,v): self.maxh=v
    def height(self): return self.h
    def width(self): return self.w
    def resize(self,w,h): self.w=w; self.h=h
class AppStub:
    @staticmethod
    def primaryScreen(): return None
    @staticmethod
    def screenAt(_): return None
ns2={'QApplication':AppStub}
exec(compile(ast.Module(body=[snode,lnode],type_ignores=[]),str(main),'exec'),ns2)
p=Panel(); ck('oversized window is rescued to work area',ns2['_h86_refresh_vertical_limit'](p,True) and p.maxh==900 and p.h==900 and p.w==800)
ck('H86 note present',(root/'FRAMELESS_VERTICAL_RESIZE_RECOVERY_H86_NOTE_20260906.md').is_file())
print(f'H86 FRAMELESS VERTICAL RESIZE RECOVERY: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
