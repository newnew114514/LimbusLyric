"""H92 nav-button click-or-drag gesture replay."""
import ast, sys
from pathlib import Path
sys.dont_write_bytecode=True
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_NAV_BUTTON_DRAG_GESTURE_H92_REPLAY.py <root>')
root=Path(sys.argv[1]).resolve(); main=next(root.glob('LimbusLyric_*.py')); src=main.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def node(name):
    n=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name),None)
    if n is None: raise SystemExit('H92 missing '+name)
    return n
def text(name): return ast.get_source_segment(src,node(name)) or ''
ck('H92 build tag','+ NAV BUTTON DRAG GESTURE H92' in src)
start=src.index('# H92 navigation-button drag gesture'); end=src.index('# H93 explicit workspace grip',start); block=src[start:end]
for bad in ('MediaSessionSync.','_merge_uia_position','qq-seek-session','LyricSearchEngine','FadingLine.'):
    ck('presentation boundary excludes '+bad,bad not in block)
cls=text('H92NavButtonDragGesture')
ck('nav children receive event filters','nav.findChildren(QWidget)' in cls and 'obj.installEventFilter(self)' in cls)
ck('drag threshold is seven pixels','H92_NAV_DRAG_THRESHOLD_PX = 7' in block)
ck('vertical intent dominates horizontal jitter','abs(dy) < abs(dx)' in cls)
ck('button press stays click-capable','self.pending = True' in cls and 'return False' in cls)
ck('drag cancels pressed button',"getattr(obj, 'setDown', None)" in cls and 'self._cancel_pressed_control()' in cls)
ck('drag only adjusts H91 hero presentation','_h91_apply_hero_height' in cls and '_loaded_song =' not in cls and '_loaded_artist =' not in cls)
ck('release after drag is consumed','if self.dragging:' in cls and 'event.accept()' in cls)
ck('release without drag remains click path','PushedButton' not in cls and 'Threshold was never crossed' in cls and 'return False' in cls)
ck('H91 splitter left intact','class H91WorkspaceSplitter' in src and 'if obj is not self.nav: return False' in text('H91WorkspaceSplitter'))
ck('H92 note present',(root/'NAV_BUTTON_DRAG_GESTURE_H92_NOTE_20260906.md').is_file())

# Behavior replay with tiny Qt fakes: ordinary click is untouched, vertical drag is consumed,
# and horizontal movement does not steal navigation clicks.
class P:
    def __init__(self,x,y): self._x=x; self._y=y
    def x(self): return self._x
    def y(self): return self._y
class Ev:
    def __init__(self,t,x=0,y=0,button=1,buttons=1): self._t=t; self._p=P(x,y); self._button=button; self._buttons=buttons; self.accepted=False
    def type(self): return self._t
    def globalPos(self): return self._p
    def button(self): return self._button
    def buttons(self): return self._buttons
    def accept(self): self.accepted=True
class ObjBase:
    def __init__(self,*a): pass
class Btn:
    def __init__(self): self.filters=[]; self.down=True
    def installEventFilter(self,f): self.filters.append(f)
    def setDown(self,v): self.down=bool(v)
class Nav(Btn):
    def __init__(self,children): super().__init__(); self.children=children; self.cursor=None
    def findChildren(self,_): return list(self.children)
    def setToolTip(self,_): pass
    def setCursor(self,c): self.cursor=c
class Panel: _h91_hero_height=204
class QtFake:
    LeftButton=1; SizeVerCursor=10; SplitVCursor=11
class QEFake:
    MouseButtonPress=1; MouseMove=2; MouseButtonRelease=3
calls=[]
def apply(panel,h,persist): panel._h91_hero_height=int(h); calls.append((int(h),bool(persist))); return True
ns={'QObject':ObjBase,'_H92_QOBJECT_BASE':ObjBase,'QWidget':object,'Qt':QtFake,'QEvent':QEFake,'H91_HERO_DEFAULT_H':204,'H92_NAV_DRAG_THRESHOLD_PX':7,'_h91_apply_hero_height':apply}
exec(compile(ast.Module(body=[node('H92NavButtonDragGesture')],type_ignores=[]),str(main),'exec'),ns)
C=ns['H92NavButtonDragGesture']; b=Btn(); nav=Nav([b]); panel=Panel(); g=C(panel,nav)
ck('child button is actually watched',g in b.filters)
# click: no threshold crossing => event filter leaves both ends untouched and no hero resize
calls.clear(); b.down=True
r1=g.eventFilter(b,Ev(QEFake.MouseButtonPress,100,100)); r2=g.eventFilter(b,Ev(QEFake.MouseButtonRelease,102,102,buttons=0))
ck('short button click is untouched',r1 is False and r2 is False and not calls)
# horizontal motion: 12x / 3y should stay a click candidate
calls.clear(); b.down=True; g.eventFilter(b,Ev(QEFake.MouseButtonPress,100,100)); rh=g.eventFilter(b,Ev(QEFake.MouseMove,112,103)); rr=g.eventFilter(b,Ev(QEFake.MouseButtonRelease,112,103,buttons=0))
ck('horizontal jitter does not steal click',rh is False and rr is False and not calls)
# vertical drag: 11 px should promote, cancel button down, resize hero, and consume release
calls.clear(); panel._h91_hero_height=204; b.down=True; g.eventFilter(b,Ev(QEFake.MouseButtonPress,100,100)); rm=g.eventFilter(b,Ev(QEFake.MouseMove,101,111)); re=g.eventFilter(b,Ev(QEFake.MouseButtonRelease,101,111,buttons=0))
ck('vertical button drag promotes to splitter',rm is True and re is True and panel._h91_hero_height==215)
ck('vertical drag cancels pending button click',b.down is False)
ck('drag release persists resulting hero height',calls and calls[-1]==(215,True))
print(f'H92 NAV BUTTON DRAG GESTURE: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
