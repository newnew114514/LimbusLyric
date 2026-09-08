#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_PREVIEW_FIT_CLASSIC_COMPACT_FRONTEND_H95F3_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
marker='# H95F3 preview fit + classic compact frontend'
need(marker in src,'H95F3 marker missing')
need('+ PREVIEW FIT + CLASSIC COMPACT FRONTEND H95F3' in src,'H95F3 build tag missing')
start=src.index(marker); end=src.index('# H95F4 true legacy frontend',start); block=src[start:end]
for bad in ('MediaSessionSync.','LyricWindow._playback_position =','LyricSearchEngine.search =','parse_lrc =','_h91_fetch_qq_art='):
    need(bad not in block,'H95F3 crossed presentation boundary: '+bad)
# Execute pure geometry/profile helpers from the real source.
wanted={'_h95f3_preview_geometry','_h95f3_layout_profile'}
nodes={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted}
need(set(nodes)==wanted,'H95F3 pure helpers missing')
ns={
 'H95F3_PREVIEW_STAGE_H':108,'H95F3_PREVIEW_OPEN_CARD_H':154,'H95F3_PREVIEW_OPEN_HOST_H':176,
 'H95F3_LEGACY_TOP_NAV_H':36,'H95F3_STUDIO_TOP_NAV_H':43,
}
for name in ('_h95f3_preview_geometry','_h95f3_layout_profile'):
    exec(compile(ast.Module(body=[nodes[name]],type_ignores=[]),'<h95f3-pure>','exec'),ns)
g=ns['_h95f3_preview_geometry'](True)
need(g['stage']>=104,'preview stage remains too short for metric footer')
need(g['card']>=g['stage']+44,'preview card does not budget header/spacing/footer')
need(g['host']>=g['card']+18,'preview host does not budget outer margins')
legacy=ns['_h95f3_layout_profile']('legacy'); studio=ns['_h95f3_layout_profile']('studio')
need(legacy['mode']=='legacy' and not legacy['workspace_copy'],'legacy mode did not retire editorial workspace copy')
need(legacy['top_nav_h']<studio['top_nav_h'],'legacy mode is not denser than studio')
need(legacy['card_spacing']<=7 and legacy['card_margins'][0]<=10,'legacy card density not compact')
need(studio['mode']=='studio' and studio['workspace_copy'],'studio mode lost current workspace header')
# User-facing selector and persistence: independent of H87 rose/forest palette.
need("combo.addItem('新版','studio')" in block and "combo.addItem('旧版','legacy')" in block,'layout selector options must use exact 新版/旧版 names')
need("title=QLabel('前端布局'" in block,'layout selector not installed under Appearance')
need("settings['h95f3_frontend_layout']" in block,'layout preference not persisted')
need("panel.main_tabs.widget(1).widget()" in block,'layout selector not attached to Appearance page')
need("globals()['H89_PREVIEW_STAGE_H']=int(H95F3_PREVIEW_STAGE_H)" in block,'preview runtime override missing')
need("globals()['H89_PREVIEW_OPEN_CARD_H']=int(H95F3_PREVIEW_OPEN_CARD_H)" in block,'preview card runtime override missing')
need("globals()['H89_PREVIEW_OPEN_HOST_H']=int(H95F3_PREVIEW_OPEN_HOST_H)" in block,'preview host runtime override missing')
need("no old frontend code is imported or reactivated" in block,'legacy implementation boundary comment missing')
need('H95F3_LAYOUT_QSS' in block and 'QWidget[h95f3Layout="legacy"]' in block,'legacy compact styling missing')
need("_h95f3_studio_hero_height" in block and "_h95f3_legacy_hero_height" in block,'per-layout Hero height memory missing')
print('PREVIEW FIT + CLASSIC COMPACT FRONTEND H95F3 REPLAY: PASS')
print('  preview footer budget: PASS')
print('  modern/legacy layout split without legacy code rollback: PASS')
print('  per-layout persistence + full modern feature ownership retained: PASS')
