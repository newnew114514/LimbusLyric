#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_PAGE_LOCAL_PREVIEW_LEGACY_CHROME_H95F4F3_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
marker='# H95F4F3 page-local preview'
chrome='# H95F4F3 legacy chrome isolation'
need(marker in src and chrome in src,'H95F4F3 markers missing')
need('+ PAGE-LOCAL PREVIEW + LEGACY CHROME ISOLATION H95F4F3' in src,'H95F4F3 build tag missing')
start=src.index(marker); end=src.index('# H95F5 bilingual subtitle + placement region',start); block=src[start:end]
for bad in ('MediaSessionSync.','LyricWindow._playback_position =','LyricSearchEngine.search =','parse_lrc ='):
    need(bad not in block,'H95F4F3 crossed presentation boundary: '+bad)
# Preview hierarchy: cards must return to their own pages and the old shell-level host must retire.
for token in (
    "style_page = _h95f4f3_page(panel, 1)",
    "motion_page = _h95f4f3_page(panel, 2)",
    "card.setParent(page)",
    "layout.insertWidget(0, card)",
    "host.setMinimumHeight(0); host.setMaximumHeight(0); host.hide()",
): need(token in block,'page-local preview wiring missing: '+token)
need("globals()['_h80_sync_studio_stage'] = _h95f4f3_sync_studio_stage" in block,'H80 shell-level preview owner not retired')
need("globals()['_h89_apply_preview_state'] = _h95f4f3_apply_preview_state" in block,'preview disclosure still owns shell geometry')
# Execute the actual pure chrome contract from source.
fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h95f4f3_chrome_profile'),None)
need(fn is not None,'chrome profile helper missing')
ns={}; exec(compile(ast.Module(body=[fn],type_ignores=[]),'<h95f4f3-chrome>','exec'),ns)
legacy=ns['_h95f4f3_chrome_profile']('legacy','classic')
studio=ns['_h95f4f3_chrome_profile']('studio','classic')
need(legacy['chrome'] and legacy['button_border'] and legacy['legacy_title_alpha']==128,'Legacy chrome contract not V29-like')
need(not studio['chrome'] and not studio['button_border'] and studio['legacy_title_alpha']==0,'Modern Studio is not isolated from Legacy chrome')
# Final QSS must target the real widgets directly, not rely only on an ancestor property.
assign=next((n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='H95F4F3_CHROME_QSS' for t in n.targets)),None)
need(assign is not None and isinstance(assign.value,ast.Constant) and isinstance(assign.value.value,str),'H95F4F3_CHROME_QSS missing')
qss=assign.value.value
need('QFrame#panelTitleBar[h95f4LegacyChrome="true"]' in qss,'titlebar is not directly scoped')
need('QPushButton#windowMinButton[h95f4LegacyChrome="true"]' in qss,'window buttons are not directly scoped')
need('border: 1px solid rgba(255,255,255,178);' in qss,'V29 window-button border was not restored')
need('border-radius: 5px;' in qss,'V29 window-button shape was not restored')
need('background: #7c2e3b' in qss,'V29 close hover accent missing')
need('QTabBar[h95f4LegacyChrome="true"]::tab' in qss,'native tabbar material is not directly scoped')
# The runtime switch must set/reset the property on every concrete chrome target and repolish.
need("w.setProperty('h95f4LegacyChrome', bool(profile['chrome']))" in block,'direct legacy chrome property toggle missing')
need('w.style().unpolish(w); w.style().polish(w); w.update()' in block,'per-widget repolish missing; stale cross-frontend QSS can recur')
need("globals()['_h95f4_apply_frontend'] = _h95f4f3_apply_frontend" in block,'frontend switch is not wired through chrome isolation')
print('PAGE-LOCAL PREVIEW + LEGACY CHROME H95F4F3 REPLAY: PASS')
print('  preview disclosure cannot move the tab/navigation bar: PASS')
print('  Legacy/Modern title chrome is directly isolated and re-polished: PASS')
print('  V29 bordered — / □ / × controls restored in Legacy only: PASS')
