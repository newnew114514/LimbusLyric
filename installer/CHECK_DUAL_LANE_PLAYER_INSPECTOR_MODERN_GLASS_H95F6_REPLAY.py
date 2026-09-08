#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, re, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_DUAL_LANE_PLAYER_INSPECTOR_MODERN_GLASS_H95F6_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
marker='# H95F6 dual-lane bilingual + player inspector + modern glass'
need(marker in src,'H95F6 marker missing')
need('+ DUAL-LANE BILINGUAL + PLAYER SYNC INSPECTOR + MODERN GLASS H95F6' in src,'H95F6 build tag missing')
start=src.index(marker); end=src.index('# H95F7 render hotpath + UI coherence',start); block=src[start:end]
for bad in ('MediaSessionSync.','LyricSearchEngine.search =','parse_lrc ='):
    need(bad not in block,'H95F6 crossed transport/provider owner: '+bad)
for token in (
    "panel.h95f6_bilingual_check=QCheckBox('原歌词 + 翻译（双语）'",
    "panel.trans_check.setText('仅显示翻译（替换原歌词）')",
    "_h75_bind_spin_proxy(panel.h95f6_translation_scale,panel.h95f5_translation_scale)",
    "old.setProperty('h75SearchIgnore',True); old.hide()",
    "title=QLabel('字幕活动区域',card)",
    "panel.h95f6_player_offset_spin=QSpinBox(frame)",
    "panel.player_combo.currentTextChanged.connect",
    "store[scoped]=row; store.pop(legacy,None)",
    "globals()['_h95_activate_song_correction']=_h95f6_activate_song_correction",
    "h95f6ModernGlass=\"true\"",
    "globals()['_h95f5_draw_secondary_text']=lambda *a,**k: False",
    "_h95f6_draw_active_translation(window,p,text)",
    "_h95f6_draw_history_translation(row,painter,saved)",
    "_h54_apply_active_depth_transform(painter, window)",
    "window.stroke_color", "window.glow_color", "window.shadow_color",
): need(token in block,'H95F6 runtime/UI integration missing: '+token)
# H95F6 intentionally keeps translation search in H95F5's mature trans-only path rather than
# introducing a second provider implementation.
need("LyricSearchEngine.search(song,artist,source,True" in src[src.index('# H95F5 bilingual subtitle + placement region'):start], 'bilingual no longer uses trans-only search primitive')

funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
def fn(name):
    need(name in funcs,'function missing: '+name); return funcs[name]

# Pure player mapping and proportional main/translation glyph mapping execute from real AST.
ns={'re':re}
exec(compile(ast.Module(body=[fn('_h95f6_player_key'),fn('_h95f6_player_label'),fn('_h95f6_main_index_for_secondary')],type_ignores=[]),'<h95f6-pure>','exec'),ns)
need(ns['_h95f6_player_key']('QQ音乐')=='qq','QQ mapping failed')
need(ns['_h95f6_player_key']('Spotify')=='spotify','Spotify mapping failed')
need(ns['_h95f6_player_key']('网易云音乐')=='netease','NetEase mapping failed')
need(ns['_h95f6_player_key']('酷狗音乐')=='kugou','KuGou mapping failed')
need([ns['_h95f6_main_index_for_secondary'](i,5,9) for i in range(5)]==[0,2,4,6,8],'secondary-to-primary animation mapping is not proportional')

# Resolved user preset font must be copied without clamping weight/italic/style: only size scales.
class FakeFont:
    Normal=50; DemiBold=63
    def __init__(self,other=None):
        if isinstance(other,FakeFont): self.size=other.size; self.weight=other.weight; self.italic=other.italic; self.family=other.family; self.px=other.px
        else: self.size=40.0; self.weight=87; self.italic=True; self.family='UserPresetFont'; self.px=-1
    def pointSizeF(self): return self.size
    def setPointSizeF(self,v): self.size=float(v)
    def pixelSize(self): return self.px
    def setPixelSize(self,v): self.px=int(v)
font_ns={'QFont':FakeFont,'H95F6_TRANSLATION_SCALE_DEFAULT':82}
exec(compile(ast.Module(body=[fn('_h95f6_lane_font')],type_ignores=[]),'<h95f6-font>','exec'),font_ns)
base=FakeFont(); out=font_ns['_h95f6_lane_font'](base,75)
need(abs(out.size-30.0)<0.001,'translation relative size not applied')
need(out.weight==87 and out.italic is True and out.family=='UserPresetFont','translation lane mutated resolved user preset style')

# Active animation state must mirror primary per-glyph fade + motion instead of using one flat alpha.
flow_ns={}
exec(compile(ast.Module(body=[fn('_h95f6_primary_flow_state')],type_ignores=[]),'<h95f6-flow>','exec'),flow_ns)
class Flow:
    _flow_fade_ranges=[(2,4,0.35)]; _flow_motion_ranges=[(2,4,11.0,-7.0)]; _flow_fade_start=-1; _flow_fade_end=-1
alpha,dx,dy=flow_ns['_h95f6_primary_flow_state'](Flow(),3,0.8)
need(abs(alpha-0.28)<1e-6 and (dx,dy)==(11.0,-7.0),'translation lane does not inherit active entrance fade/motion')

# Exit glyph behavior must independently cover the historical per-char and directional wipes.
exit_ns={'_h70_effect_key':lambda x:str(x),'_h95f6_exit_progress':lambda row:row.progress}
exec(compile(ast.Module(body=[fn('_h95f6_exit_glyph_state')],type_ignores=[]),'<h95f6-exit>','exec'),exit_ns)
class Row: alpha=255; progress=0.70; exit_effect='per_char'
a0=exit_ns['_h95f6_exit_glyph_state'](Row(),0,8)[0]; a7=exit_ns['_h95f6_exit_glyph_state'](Row(),7,8)[0]
need(a0<a7,'per-char translation exit is still flat')
Row.exit_effect='wipe_ltr'; l=exit_ns['_h95f6_exit_glyph_state'](Row(),0,8)[0]; r=exit_ns['_h95f6_exit_glyph_state'](Row(),7,8)[0]
need(l<r,'LTR translation wipe does not follow preset direction')
Row.exit_effect='wipe_rtl'; l2=exit_ns['_h95f6_exit_glyph_state'](Row(),0,8)[0]; r2=exit_ns['_h95f6_exit_glyph_state'](Row(),7,8)[0]
need(r2<l2,'RTL translation wipe does not follow preset direction')

# The H95F5 flat helper must be suppressed only during mature paint, then restored; new dual-lane draw runs.
calls={'old_secondary':0,'new_lane':0,'pre':0}
def old_secondary(*a,**k): calls['old_secondary']+=1
def pre(window,event): calls['pre']+=1; paint_ns['_h95f5_draw_secondary_text'](); return 'ok'
class Painter:
    Antialiasing=1
    def __init__(self,*a): pass
    def setRenderHint(self,*a): pass
    def end(self): pass
class Win: pass
paint_ns={'_H95F6_PAINT_PRE':pre,'_h95f5_draw_secondary_text':old_secondary,'_h95f5_translation_for_line':lambda w:'翻译','QPainter':Painter,'_h95f6_draw_active_translation':lambda w,p,t:calls.__setitem__('new_lane',calls['new_lane']+1)}
exec(compile(ast.Module(body=[fn('_h95f6_paint_event')],type_ignores=[]),'<h95f6-paint>','exec'),paint_ns)
need(paint_ns['_h95f6_paint_event'](Win(),object())=='ok','mature primary paint return changed')
need(calls=={'old_secondary':0,'new_lane':1,'pre':1},'old flat sidecar was drawn or new dual lane did not draw')
need(paint_ns['_h95f5_draw_secondary_text'] is old_secondary,'flat helper was not restored after paint')

# Sync Doctor scope migration: legacy song key migrates to selected player only, then another
# player sees no row until independently calibrated.
class Combo:
    def __init__(self,text): self.text=text
    def currentText(self): return self.text
class Panel:
    def __init__(self): self.player_combo=Combo('QQ音乐'); self._h95_sync_doctor_store={'song|artist':{'song':'Song','artist':'Artist','manual_adjust_ms':120,'anchors':[]}}
panel=Panel(); saves=[]
sync_ns={'_h95_panel_identity':lambda p:('song|artist','Song','Artist'),'_h95f6_player_key':ns['_h95f6_player_key'],'H95F6_SYNC_SCOPE_SEPARATOR':'::','_h95_normalize_correction_row':lambda row,song='',artist='':dict(row or {},song=song,artist=artist),'_h95_schedule_save':lambda p:saves.append(1),'write_error_log':lambda *a,**k:None}
exec(compile(ast.Module(body=[fn('_h95f6_sync_identity'),fn('_h95f6_sync_row')],type_ignores=[]),'<h95f6-sync>','exec'),sync_ns)
scoped,row,*_=sync_ns['_h95f6_sync_row'](panel,False)
need(scoped=='qq::song|artist' and isinstance(row,dict),'legacy correction did not migrate to QQ scope')
need('song|artist' not in panel._h95_sync_doctor_store and 'qq::song|artist' in panel._h95_sync_doctor_store,'unscoped correction still leaks across players')
panel.player_combo.text='Spotify'; scoped2,row2,*_=sync_ns['_h95f6_sync_row'](panel,False)
need(scoped2=='spotify::song|artist' and row2 is None,'QQ correction leaked into Spotify scope')

# Current-player inspector replay: switching players loads their stored spin values without changing them.
class Spin:
    def __init__(self,v=0): self.v=v; self.enabled=True; self.block=False
    def value(self): return self.v
    def setValue(self,v): self.v=int(v)
    def blockSignals(self,b): self.block=b
    def setEnabled(self,b): self.enabled=bool(b)
class Label:
    def __init__(self): self.text=''
    def setText(self,t): self.text=str(t)
class InspectorPanel:
    def __init__(self):
        self.player_combo=Combo('QQ音乐'); self.qq_sync_offset_spin=Spin(175); self.spotify_sync_offset_spin=Spin(-90); self.netease_sync_offset_spin=Spin(25); self.kugou_sync_offset_spin=Spin(0); self.h95f6_player_offset_spin=Spin(); self.h95f6_player_offset_label=Label(); self.h95f6_player_hint=Label()
ip=InspectorPanel()
ins_ns={'_h95f6_player_key':ns['_h95f6_player_key'],'_h95f6_player_label':ns['_h95f6_player_label'],'_h95f6_sync_source_spin':None,'_h95f6_activate_song_correction':lambda p:None,'_h95f6_refresh_sync_doctor_ui':lambda p:None}
exec(compile(ast.Module(body=[fn('_h95f6_sync_source_spin'),fn('_h95f6_refresh_player_inspector')],type_ignores=[]),'<h95f6-inspector>','exec'),ins_ns)
ins_ns['_h95f6_refresh_player_inspector'](ip); need(ip.h95f6_player_offset_spin.value()==175 and 'QQ音乐' in ip.h95f6_player_offset_label.text,'QQ inspector did not load QQ history')
ip.player_combo.text='Spotify'; ins_ns['_h95f6_refresh_player_inspector'](ip); need(ip.h95f6_player_offset_spin.value()==-90 and 'Spotify' in ip.h95f6_player_offset_label.text,'Spotify inspector did not restore its independent history')

# Modern glass must be translucent but remain more substantial than legacy chrome; it must
# be scoped to an explicit modern property so Legacy is untouched.
m1=re.search(r'panelTitleBar\[h95f6ModernGlass="true"\]\[h95f4Palette="classic"\].*?rgba\(10,10,13,(\d+)\)',block,re.S)
m2=re.search(r'panelTitleBar\[h95f6ModernGlass="true"\]\[h95f4Palette="studio"\].*?rgba\(12,18,17,(\d+)\)',block,re.S)
need(m1 and m2,'modern glass alpha rules missing')
need(140<int(m1.group(1))<210 and 140<int(m2.group(1))<210,'modern title bar is still effectively opaque or too transparent')
need("bar.setProperty('h95f6ModernGlass',bool(modern))" in block,'modern/legacy glass scope is not repolished on real title bar')

print('DUAL-LANE + PLAYER INSPECTOR + MODERN GLASS H95F6 REPLAY: PASS')
print('  translation inherits resolved preset + active entrance state: PASS')
print('  translation per-char/wipe exit lifecycle: PASS')
print('  flat H95F5 sidecar suppressed without hiding dirty-region geometry: PASS')
print('  player-scoped Sync Doctor migration/isolation: PASS')
print('  current-player offset inspector persistence switching: PASS')
print('  modern title glass scope/opacity: PASS')
