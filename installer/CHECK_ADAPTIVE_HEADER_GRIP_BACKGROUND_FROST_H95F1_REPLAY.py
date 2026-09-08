#!/usr/bin/env python3
from __future__ import annotations
import ast
import pathlib
import sys

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_ADAPTIVE_HEADER_GRIP_BACKGROUND_FROST_H95F1_REPLAY.py <main.py>')
path=pathlib.Path(sys.argv[1]).resolve()
src=path.read_text(encoding='utf-8')
tree=ast.parse(src)

def need(cond,msg):
    if not cond: raise AssertionError(msg)

marker='# H95F1 adaptive header + grip micro interaction + background frost'
need(marker in src,'H95F1 marker missing')
need('+ ADAPTIVE HEADER + GRIP MICRO INTERACTION + BACKGROUND FROST H95F1' in src,'H95F1 build tag missing')
next_marker='# H95F2 frost material + cover identity + Hero collision closure'
need(next_marker in src,'H95F2 boundary marker missing')
block=src[src.index(marker):src.index(next_marker,src.index(marker))]
for bad in ('MediaSessionSync.','LyricSearchEngine.search =','LyricWindow._playback_position =','parse_lrc ='):
    need(bad not in block,'H95F1 crossed protected playback/lyric boundary: '+bad)

# Execute the pure responsive and frost sizing policies from the actual main program.
wanted={'_h95f1_header_profile','_h95f1_frost_downsample_size'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted]
need({n.name for n in nodes}==wanted,'H95F1 pure helpers missing')
ns={
    'H93_HERO_MIN_H':28,'H91_HERO_MAX_H':252,'H95F1_HERO_DEFAULT_H':176,
}
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<h95f1-pure>','exec'),ns)
profile=ns['_h95f1_header_profile']
roomy=profile(176,900,100); light=profile(156,900,100); tight=profile(108,900,100); mini=profile(72,900,100); collapsed=profile(28,900,100)
need(roomy['show_manager'] and roomy['show_detail'] and roomy['show_title'],'default Hero lost primary/secondary information')
need(light['show_manager'] and light['show_detail'] and light['show_title'],'light upward drag hides content too early')
need(tight['show_title'] and tight['show_detail'] and not tight['show_manager'],'tight stage priority wrong')
need(mini['show_title'] and not mini['show_detail'],'mini stage must preserve song title after secondary detail retires')
need(not collapsed['show_title'],'near-collapsed Hero should finally retire title')
need(roomy['title_px'] > light['title_px'] >= tight['title_px'] > mini['title_px'] >= collapsed['title_px'],'title does not progressively scale')
need(roomy['margins'][1] > tight['margins'][1] >= mini['margins'][1],'vertical whitespace does not compress progressively')
need(roomy['progress_h'] > tight['progress_h'] >= mini['progress_h'],'hero progress rail does not shrink')

frost=ns['_h95f1_frost_downsample_size']
need(frost(1600,900,0)==(1600,900),'0 frost must preserve source size')
a=frost(1600,900,25); b=frost(1600,900,60); c=frost(1600,900,100)
need(1600>a[0]>b[0]>c[0]>=24 and 900>a[1]>b[1]>c[1]>=24,'frost amount is not monotonic')

# Persistent/user-facing background contract.
need("'background_blur': panel.background_blur_slider.value()" in src,'background frost persistence missing')
need("settings.get('background_blur', 0)" in src,'background frost restore missing')
need('self.background_blur_slider.setRange(0, 100)' in src,'background frost full-settings slider missing')
need(block.count("QLabel('背景磨砂')") >= 0 and src.count('背景磨砂') >= 3,'background frost not exposed with background strength')
need("panel.panel_background.set_background(getattr(panel,'_background_path',''),enabled,strength,blur)" in block,'background application does not receive frost amount')
need("ControlPanel._apply_background=_h95f1_apply_background" in block,'H95F1 background wrapper not installed')

# Density defaults + explicit grip feedback contract.
need('H95F1_HERO_DEFAULT_H = 176' in block,'dense default Hero height missing')
need("settings['h95f1_header_density_migrated']=True" in block,'one-time legacy 204px migration missing')
need('H95F1_GRIP_ROW_H = 16' in block,'grip passive row was not tightened')
need('H95F1_WORKSPACE_TOP_MARGIN = 7' in block and 'H95F1_WORKSPACE_BOTTOM_MARGIN = 6' in block,'workspace header density missing')
need("grip.setToolTip('')" in block,'instructional grip tooltip not retired')
need('H95F1_GRIP_HOVER_W = 56' in block and 'H95F1_GRIP_ACTIVE_W = 60' in block,'grip micro-interaction sizes missing')
need('H93_GRIP_HIT_HEIGHT' in block,'compact hit target relationship missing')

# Execute actual micro-interaction class against tiny Qt boundary fakes.
cls=next((n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='H95F1GripMicroInteraction'),None)
need(cls is not None,'grip micro-interaction class missing')
class ObjBase:
    def __init__(self,*a,**k): pass
class QtFake: LeftButton=1
class QEventFake:
    Enter=10; Leave=11; MouseButtonPress=12; MouseButtonRelease=13; WindowDeactivate=14; ApplicationDeactivate=15
class Mark:
    def __init__(self): self.size=None; self.style=''
    def setFixedSize(self,w,h): self.size=(w,h)
    def setStyleSheet(self,s): self.style=s
class Grip:
    def __init__(self): self.filters=[]; self.tip='x'; self.hover=False
    def installEventFilter(self,f): self.filters.append(f)
    def setToolTip(self,s): self.tip=s
    def underMouse(self): return self.hover
class Event:
    def __init__(self,k,button=None): self.k=k; self.b=button
    def type(self): return self.k
    def button(self): return self.b
fake_ns={'_H95F1_QOBJECT_BASE':ObjBase,'Qt':QtFake,'QEvent':QEventFake,
         'H95F1_GRIP_ACTIVE_W':60,'H95F1_GRIP_ACTIVE_H':4,'H95F1_GRIP_HOVER_W':56,'H95F1_GRIP_HOVER_H':4,
         'H93_GRIP_LINE_WIDTH':52,'H93_GRIP_LINE_HEIGHT':3}
exec(compile(ast.Module(body=[cls],type_ignores=[]),'<h95f1-grip>','exec'),fake_ns)
g=Grip(); m=Mark(); f=fake_ns['H95F1GripMicroInteraction'](object(),g,m)
need(g.tip=='' and m.size==(52,3),'idle grip visual/tool-tip contract wrong')
g.hover=True; f.eventFilter(g,Event(QEventFake.Enter)); need(m.size==(56,4),'hover does not gently enlarge grip')
f.eventFilter(g,Event(QEventFake.MouseButtonPress,QtFake.LeftButton)); need(m.size==(60,4),'press does not strengthen grip feedback')
f.eventFilter(g,Event(QEventFake.MouseButtonRelease,QtFake.LeftButton)); need(m.size==(56,4),'release under pointer does not return to hover state')
g.hover=False; f.eventFilter(g,Event(QEventFake.Leave)); need(m.size==(52,3),'leave does not restore idle grip')

print('ADAPTIVE HEADER + GRIP + BACKGROUND FROST H95F1 REPLAY: PASS')
print('  progressive Hero compression / primary-title-last policy: PASS')
print('  compact explicit grip hover/press feedback, no instructional tooltip: PASS')
print('  persistent custom-background strength + frost controls: PASS')
