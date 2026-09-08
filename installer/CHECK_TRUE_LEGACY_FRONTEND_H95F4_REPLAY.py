#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_TRUE_LEGACY_FRONTEND_H95F4_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
marker='# H95F4 true legacy frontend'
need(marker in src,'H95F4 marker missing')
need('+ TRUE LEGACY FRONTEND H95F4' in src,'H95F4 build tag missing')
start=src.index(marker); end=src.index('# H95F4F1 startup re-entry closure',start); block=src[start:end]
# H95F4 is shell-only and must not take playback/lyrics authority.
for bad in ('MediaSessionSync.', 'LyricWindow._playback_position =', 'LyricSearchEngine.search =', 'parse_lrc =', '_h91_fetch_qq_art='):
    need(bad not in block,'H95F4 crossed presentation boundary: '+bad)
# Execute the real pure visibility contract.
fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h95f4_frontend_profile'),None)
need(fn is not None,'frontend profile helper missing')
ns={}; exec(compile(ast.Module(body=[fn],type_ignores=[]),'<h95f4-profile>','exec'),ns)
legacy=ns['_h95f4_frontend_profile']('legacy'); studio=ns['_h95f4_frontend_profile']('studio')
need(legacy['legacy_header'] and not legacy['modern_hero'],'legacy must replace, not compact, the modern record Hero')
need(not legacy['top_nav'] and not legacy['workspace_header'] and not legacy['workspace_grip'],'legacy still exposes modern Studio shell landmarks')
need(legacy['native_tabbar'],'legacy must restore QTabWidget native tab bar')
need(studio['modern_hero'] and studio['top_nav'] and studio['workspace_header'] and studio['workspace_grip'],'Studio shell restore contract incomplete')
need(not studio['native_tabbar'],'Studio should keep current custom top navigation')
# Actual application path must wire those contract decisions to real widgets.
for token in (
    "hero.setVisible(bool(profile['modern_hero']))",
    "legacy_header.setVisible(bool(profile['legacy_header']))",
    "nav.setVisible(bool(profile['top_nav']))",
    "header.setVisible(bool(profile['workspace_header']))",
    "grip.setVisible(bool(profile['workspace_grip']))",
    "panel.main_tabs.tabBar().setVisible(bool(profile['native_tabbar']))",
): need(token in block,'real visibility wiring missing: '+token)
# The H95F3 selector that accidentally landed in the Appearance/Subtitle page must be retired.
need("card=getattr(panel,'h95f3_layout_card',None)" in block and "card.hide()" in block,'old in-page H95F3 selector is not retired')
# User requested the switch in the top-right Interface popup.
need("section=QLabel('前端版本',dlg)" in block,'Interface popup frontend-version section missing')
need("combo.addItem('新版','studio')" in block and "combo.addItem('旧版','legacy')" in block,'Interface popup frontend options must use exact 新版/旧版 names')
need("panel._h73_show_background_popup=lambda p=panel:_h95f4_show_interface_popup(p)" in block,'top-right Interface button not routed to H95F4 popup')
need("globals()['_h95f1_apply_shell_density']=_h95f4_apply_shell_density" in block,'resize/density pass can escape Legacy shell')
need("panel.main_tabs.currentChanged.connect" in block and '_h95f4_reconcile_page_shell' in block,'page changes can re-expose Studio rail/header in Legacy')
# V29 visual language anchors: simple header, old labels, square/top-rule cards, no record in Legacy.
need("H95F4_LEGACY_TAB_LABELS = ('播放', '字幕', '动效', '高级', '单曲DIY')" in block,'V29 tab labels missing')
need('QFrame#h95f4LegacyHeader' in block and 'QTabWidget#mainTabs::pane' in block and 'border-top:1px solid #2b282a' in block,'V29-inspired shell styling missing')
need("settings['h95f4_frontend_version']" in block,'frontend-version persistence missing')
print('TRUE LEGACY FRONTEND H95F4 REPLAY: PASS')
print('  legacy replaces Studio landmarks instead of compacting them: PASS')
print('  top-right Interface selector + persistence: PASS')
print('  modern runtime owners retained; old shell language restored: PASS')
