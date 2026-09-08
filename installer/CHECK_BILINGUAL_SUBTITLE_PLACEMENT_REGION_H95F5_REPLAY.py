#!/usr/bin/env python3
from __future__ import annotations
import ast, bisect, pathlib, re, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_BILINGUAL_SUBTITLE_PLACEMENT_REGION_H95F5_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
marker='# H95F5 bilingual subtitle + placement region'
need(marker in src,'H95F5 marker missing')
need('+ BILINGUAL SUBTITLE + PLACEMENT REGION H95F5' in src,'H95F5 build tag missing')
start=src.index(marker); end=src.index('# H95F6 dual-lane bilingual + player inspector + modern glass',start); block=src[start:end]
for bad in ('MediaSessionSync.','LyricWindow._playback_position =','LyricSearchEngine.search =','parse_lrc ='):
    need(bad not in block,'H95F5 crossed protected owner: '+bad)
for token in (
    "panel.h95f5_bilingual_combo.addItem('仅原歌词','original')",
    "panel.h95f5_bilingual_combo.addItem('原歌词 + 翻译','bilingual')",
    "panel.trans_check.setText('仅显示翻译（替换原歌词）')",
    "panel.h95f5_region_combo.addItem('仅上半屏','upper')",
    "panel.h95f5_region_combo.addItem('仅下半屏','lower')",
    "panel.h95f5_region_combo.addItem('自定义范围','custom')",
    "layout.insertWidget(min(1,layout.count()),card)",
    "LyricSearchEngine.search(song,artist,source,True",
    "prefer_precise=False",
    "window._h95f5_translation_lrc",
    "row._h95f5_translation",
    "LyricWindow._active_visual_region=_h95f5_active_visual_region",
    "LyricWindow._held_visual_region=_h95f5_held_visual_region",
    "panel._h95f5_translation_inflight",
    "_h95f5_reconcile_active_group(panel.lyric_window)",
): need(token in block,'H95F5 user/runtime wiring missing: '+token)
# Pure region + translation alignment helpers execute from the real source AST.
wanted={'_h95f5_norm_region','_h95f5_normalize_custom_percent','_h95f5_region_rect_px','_h95f5_box_outside','_h95f5_align_translation_lines','_h95f5_anchor_limits'}
nodes={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted}
need(set(nodes)==wanted,'H95F5 pure helpers missing')
body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted]
ns={'H95F5_REGION_CUSTOM_DEFAULT':(5,95,8,92),'H95F5_REGION_SAFE_DEFAULT':2,'H95F5_TRANSLATION_ALIGN_TOLERANCE_MS':900,'bisect':bisect,'re':re}
exec(compile(ast.Module(body=body,type_ignores=[]),'<h95f5-pure>','exec'),ns)
norm=ns['_h95f5_normalize_custom_percent'](90,20,95,10)
need(norm==(90.0,95.0,95.0,100.0),'invalid custom bounds are not normalized safely')
rr=ns['_h95f5_region_rect_px'](1000,800,'upper',5,95,8,92,0)
need(rr==(0.0,0.0,1000.0,400.0),'upper-half region wrong')
rr=ns['_h95f5_region_rect_px'](1000,800,'lower',5,95,8,92,5)
need(rr==(50.0,440.0,950.0,760.0),'lower-half safe margin wrong')
rr=ns['_h95f5_region_rect_px'](1000,800,'custom',10,80,20,70,0)
need(rr==(100.0,160.0,800.0,560.0),'custom percentage mapping wrong')
need(ns['_h95f5_box_outside']((120,180,780,540),rr)==0.0,'valid custom box rejected')
need(ns['_h95f5_box_outside']((50,180,780,540),rr)>0.0,'out-of-region box accepted')
limits=ns['_h95f5_anchor_limits']((200,200,500,300),250,220,(100,100,800,400))
need(limits==(150.0,550.0,120.0,320.0,True,True),'anchor fit limits wrong')
limits=ns['_h95f5_anchor_limits']((0,0,1200,100),0,0,(100,100,900,500))
need(limits[4] is False and abs(limits[0]+100.0)<0.01,'oversized group centering fallback wrong')
main=[{'start_ms':1000,'text':'hello'},{'start_ms':3000,'text':'world'},{'start_ms':5000,'text':'same'}]
trans=[(1020,'你好',None),(2950,'世界',None),(5000,'same',None)]
aligned=ns['_h95f5_align_translation_lines'](main,trans)
need(aligned==['你好','世界',''],'translation line alignment/duplicate suppression wrong')
# Placement must keep the mature H61 result/angle/depth but call it only once. H95F5 then
# re-scores anchors inside the region; this avoids N-fold H61 CPU/log bursts.
place_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h95f5_place_randomly')
place_src=ast.get_source_segment(src,place_node) or ''
need(place_src.count('_H95F5_PLACE_PRE(window)')==1,'mature placement is called more than once per lyric birth')
need('_h95f5_relocate_group(window,rect' in place_src,'region anchor relocation missing')
need('mature_calls=1' in place_src,'placement logging does not prove single mature call')
reloc_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h95f5_relocate_group')
reloc_src=ast.get_source_segment(src,reloc_node) or ''
need("recent[-1]=entry" in reloc_src,'final constrained anchor is not written back to density memory')

# Execute the real relocation function with only rendering geometry stubbed. This verifies
# a late translation is pulled back into the selected region and density memory follows it.
reloc_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h95f5_relocate_group')
class FakeWindow:
    def __init__(self):
        self.x=900; self.y=700; self.angle=0; self.full_text='hello'; self._placement_recent=[(100.0,100.0,0.0),(950.0,720.0,0.0)]
    def _placement_obstacles(self): return []
    def _placement_overlap_ratio(self,a,b): return 0.0
    def _placement_box_center(self,b): return ((b[0]+b[2])*0.5,(b[1]+b[3])*0.5)
    def _placement_box(self,text,x,y,angle): return (float(x),float(y),float(x)+100.0,float(y)+40.0)
    def compute_perspective(self): self.perspective_recomputed=True
reloc_ns={'_h95f5_translation_for_line':lambda w:'翻译','_h95f5_group_box':lambda w,x,y,a,t:(float(x),float(y),float(x)+100.0,float(y)+40.0),'_h95f5_box_outside':ns['_h95f5_box_outside'],'_h95f5_anchor_limits':ns['_h95f5_anchor_limits'],'random':__import__('random'),'math':__import__('math')}
exec(compile(ast.Module(body=[reloc_node],type_ignores=[]),'<h95f5-relocate>','exec'),reloc_ns)
w=FakeWindow(); moved,before,after=reloc_ns['_h95f5_relocate_group'](w,(0.0,0.0,1000.0,400.0),'翻译',explore=False)
need(moved and before>0 and after==0.0 and 0<=w.y<=360,'late translation minimal region reconciliation failed')
need(abs(w._placement_recent[-1][1]-(w.y+20.0))<0.01,'density memory did not follow final constrained anchor')

# Execute the real placement wrapper with mature placement stubbed: one lyric birth must
# call H61 exactly once and then delegate only to the lightweight region relocator.
place_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h95f5_place_randomly')
calls={'mature':0,'relocate':0}
class PlaceWindow:
    _h95f5_region_mode='upper'; _h95f5_region_safe=0; _h95f5_region_left=5; _h95f5_region_right=95; _h95f5_region_top=8; _h95f5_region_bottom=92
    def width(self): return 1000
    def height(self): return 800
pw=PlaceWindow()
def mature(w): calls['mature']+=1
def relocate(w,rect,translation,explore=True): calls['relocate']+=1; return (True,10.0,0.0)
place_ns={'_H95F5_PLACE_PRE':mature,'_h95f5_norm_region':ns['_h95f5_norm_region'],'H95F5_REGION_SAFE_DEFAULT':2,'_h95f5_region_rect_px':ns['_h95f5_region_rect_px'],'_h95f5_translation_for_line':lambda w:'翻译','_h95f5_relocate_group':relocate,'write_error_log':lambda *a,**k:None}
exec(compile(ast.Module(body=[place_node],type_ignores=[]),'<h95f5-place>','exec'),place_ns); place_ns['_h95f5_place_randomly'](pw)
need(calls=={'mature':1,'relocate':1},'region wrapper reran mature placement or skipped lightweight relocation')

# Bilingual must be a sidecar: primary text stays full_text and precise word timing remains owned by H95.
need('main_text=window.full_text' in block,'bilingual display stopped grouping with primary line')
need('_h95f5_translation_for_line(window)' in block,'active translation does not come from unified line sidecar')
# Async translation must dedupe and late arrival must reconcile the active group inside the region.
need("_h95f5_translation_inflight','') or '')==identity" in block,'duplicate translation fetch guard missing')
need("QTimer.singleShot(0,lambda p=panel:_h95f5_schedule_translation_fetch(p))" in block,'startup bilingual fetch is not deferred after bridge installation')
need('_h95f5_reconcile_active_group(window); window.update()' in block,'cached late translation cannot reconcile active placement')
need('_h95f5_apply_history_group_transform(row,painter)' in block,'history translation does not follow row-level exit/perspective transform')
need("painter.setTransform(transform,True)" in block,'history translation lost perspective/depth transform')
print('BILINGUAL SUBTITLE + PLACEMENT REGION H95F5 REPLAY: PASS')
print('  upper/lower/custom percentage placement contract: PASS')
print('  one mature placement + bounded in-region anchor re-score: PASS')
print('  original precise line + line-level translation sidecar: PASS')
print('  translation fetch dedupe + late-sidecar reconciliation: PASS')
