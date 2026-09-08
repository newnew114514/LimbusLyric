"""H93 explicit workspace grip replay."""
import ast, sys
from pathlib import Path
sys.dont_write_bytecode=True
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_EXPLICIT_WORKSPACE_GRIP_H93_REPLAY.py <root>')
root=Path(sys.argv[1]).resolve(); main=next(root.glob('LimbusLyric_*.py')); src=main.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def node(name):
    n=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name),None)
    if n is None: raise SystemExit('H93 missing '+name)
    return n
def text(name): return ast.get_source_segment(src,node(name)) or ''
ck('H93 build tag','+ EXPLICIT WORKSPACE GRIP H93' in src and '+ COMPACT GRIP HIT TARGET H93F2' in src)
ck('real Qt QObject is imported for event filters','from PyQt5.QtCore import' in src and 'QObject' in src.split('from PyQt5.QtCore import',1)[1].split('\n',1)[0])
start=src.index('# H93 explicit workspace grip'); end=src.index('# H94 Spotify lyric fallback',start); block=src[start:end]
for bad in ('MediaSessionSync.','_merge_uia_position','qq-seek-session','LyricSearchEngine','FadingLine.'):
    ck('presentation boundary excludes '+bad,bad not in block)
cls=text('H93WorkspaceGrip'); install=text('_h93_install_workspace_grip'); retire=text('_h93_retire_inferred_nav_drag')
ck('explicit grip row is inserted after top nav',"layout.indexOf(nav)" in install and 'layout.insertWidget(max(0, nav_index + 1), row)' in install)
ck('drag hit target is compact and centered','H93_GRIP_HIT_WIDTH = 72' in block and 'H93_GRIP_HIT_HEIGHT = 14' in block and 'grip.setFixedSize(int(H93_GRIP_HIT_WIDTH), int(H93_GRIP_HIT_HEIGHT))' in install and 'row_layout.addWidget(grip, 0, Qt.AlignCenter)' in install)
ck('full-width row is passive','H93WorkspaceGrip(panel, grip)' in install and 'H93WorkspaceGrip(panel, row)' not in install)
ck('grip owns mouse during drag','grabMouse()' in cls and 'releaseMouse()' in cls)
ck('drag has application capture fallback','installEventFilter(self)' in cls and 'removeEventFilter(self)' in cls)
ck('visible mark is independent from compact hit target','H93_GRIP_LINE_WIDTH = 52' in block and 'H93_GRIP_LINE_HEIGHT = 3' in block and 'h93WorkspaceGripMark' in install)
ck('hero can near-collapse without zero fallback','H93_HERO_MIN_H = 28' in block and 'H91_HERO_MIN_H = H93_HERO_MIN_H' in block)
ck('drag directly adjusts hero','_h91_apply_hero_height' in cls and 'self.start_h + dy' in cls)
ck('double click restores default','MouseButtonDblClick' in cls and 'H91_HERO_DEFAULT_H' in cls)
ck('old inferred nav filters retired','removeEventFilter(old)' in retire and 'removeEventFilter(old2)' in retire)
ck('nav returns click only','Qt.ArrowCursor' in retire and 'Qt.PointingHandCursor' in retire)
ck('startup palette is reconciled in final init layer','def _h93_restore_persisted_frontend_theme' in block and "settings.get('h87_frontend_theme'" in block and '_h93_restore_persisted_frontend_theme(panel)' in block and 'QTimer.singleShot(0' in block)
ck('H93 note present',(root/'EXPLICIT_WORKSPACE_GRIP_H93_NOTE_20260906.md').is_file())

# Behavior replay with minimal Qt fakes.
class P:
    def __init__(self,y): self._y=y
    def y(self): return self._y
class Ev:
    def __init__(self,t,y=0,button=1,buttons=1): self._t=t; self._p=P(y); self._button=button; self._buttons=buttons; self.accepted=False
    def type(self): return self._t
    def globalPos(self): return self._p
    def button(self): return self._button
    def buttons(self): return self._buttons
    def accept(self): self.accepted=True
class ObjBase:
    def __init__(self,*a): pass
class Grip:
    def __init__(self): self.filters=[]; self.grabbed=False
    def installEventFilter(self,f): self.filters.append(f)
    def setCursor(self,_): pass
    def setToolTip(self,_): pass
    def grabMouse(self): self.grabbed=True
    def releaseMouse(self): self.grabbed=False
class Panel: _h91_hero_height=204
class QtFake:
    LeftButton=1; SplitVCursor=11
class QEFake:
    MouseButtonDblClick=0; MouseButtonPress=1; MouseMove=2; MouseButtonRelease=3
calls=[]
def apply(panel,h,persist): panel._h91_hero_height=int(h); calls.append((int(h),bool(persist))); return True
ns={'QObject':ObjBase,'_H93_QOBJECT_BASE':ObjBase,'Qt':QtFake,'QEvent':QEFake,'H91_HERO_DEFAULT_H':204,'_h91_apply_hero_height':apply}
exec(compile(ast.Module(body=[node('H93WorkspaceGrip')],type_ignores=[]),str(main),'exec'),ns)
C=ns['H93WorkspaceGrip']; panel=Panel(); grip=Grip(); g=C(panel,grip)
ck('grip filter actually installed',g in grip.filters)
calls.clear(); rp=g.eventFilter(grip,Ev(QEFake.MouseButtonPress,500)); rm=g.eventFilter(grip,Ev(QEFake.MouseMove,450)); rr=g.eventFilter(grip,Ev(QEFake.MouseButtonRelease,450,buttons=0))
ck('upward drag shrinks hero',rp is True and rm is True and rr is True and panel._h91_hero_height==154)
ck('drag captures and releases pointer',grip.grabbed is False)
ck('release persists hero height',calls and calls[-1]==(154,True))
print(f'H93 EXPLICIT WORKSPACE GRIP: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
