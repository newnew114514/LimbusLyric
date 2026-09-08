from pathlib import Path
import ast, sys, textwrap
if len(sys.argv)<2: raise SystemExit('usage: CHECK_EDITORIAL_POLISH_WIPE_BLUR_RECOVERY_H76_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines(); root=p.parent
def fail(m): raise SystemExit('H76 FAIL: '+m)
def need(t,m):
    if t not in src: fail(m+': '+repr(t))
def fn(n):
    for x in ast.walk(tree):
        if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==n: return x
    fail('function not found: '+n)
def fsrc(n):
    x=fn(n); return textwrap.dedent('\n'.join(lines[x.lineno-1:x.end_lineno]))
need('+ EDITORIAL POLISH + WIPE REFINEMENT + BLUR RECOVERY H76','build tag')
need('# H76 editorial polish + wipe refinement + blur recovery','marker')
for n in ('_h76_palette_icon','_h76_refresh_multiscreen_visibility','_h76_sync_background_button','_h76_animate_current_tab','_h76_finish_popup_motion','_h76_show_background_popup','_h76_control_init','_h76_wipe_fragment_draw','_h76_blur_release_progress','_h76_promote_orphan_history_blur','_h76_schedule_orphan_history_blur_release','_h76_safe_blur_progress','_h76_finalize_blur_retire','_h76_fading_update','_h76_activate_runtime','_h76_activate_ui'): fn(n)
if not (src.rindex("if '_h75_activate_ui' in globals():") < src.rindex("if '_h76_activate_ui' in globals():")): fail('H76 UI must activate after H75')
block=src[src.index('# H76 editorial polish + wipe refinement + blur recovery'):]
if '# H77 application shell + inspector system' in block:
    block=block[:block.index('# H77 application shell + inspector system')]
else:
    block=block[:block.index('if __name__ == \"__main__\":')]
for bad in ('MediaSessionSync.', 'LyricSearchEngine.', '_commit_seek', '_on_seek', 'requests.', 'threading.Thread(', 'QImage(', 'QPixmap.fromImage(', 'history_lines.append('):
    if bad in block: fail('crossed H76 boundary: '+bad)
ui=fsrc('_h76_control_init')
for tok in ("_h76_find_label(panel,'退场质感：')", "mode.hide()", "_h76_find_label(panel,'字幕显示屏幕：')", '_h76_refresh_multiscreen_visibility(panel)', 'panel.background_check.toggled.connect', 'panel.main_tabs.currentChanged.connect(panel._animate_current_tab)'):
    if tok not in ui: fail('UI cleanup missing '+tok)
ms=fsrc('_h76_refresh_multiscreen_visibility')
if 'visible=len(screens)>1' not in ms or 'combo.setVisible(visible)' not in ms: fail('multiscreen selector is not conditional')
bg=fsrc('_h76_sync_background_button')
for tok in ("btn.setText('背景')", 'Qt.ToolButtonTextBesideIcon', '_h76_palette_icon'):
    if tok not in bg: fail('background utility is not discoverable '+tok)

motion=fsrc('_h76_animate_current_tab')
for tok in ('H76_UI_PAGE_SETTLE_MS','effect.setOpacity(0.84)','QEasingCurve.OutCubic'):
    if tok not in motion: fail('page motion token missing '+tok)
popup=fsrc('_h76_show_background_popup')
for tok in ('H76_UI_POPUP_ENTER_MS','H76_UI_POPUP_RISE_PX',"QPropertyAnimation(effect,b'opacity'","QPropertyAnimation(dlg,b'pos'"):
    if tok not in popup: fail('popup motion token missing '+tok)
w=fsrc('_h76_wipe_fragment_draw')
for tok in ("effect not in ('wipe_ltr','wipe_rtl')", 'H76_WIPE_GHOST_MAX_ALPHA', 'H76_WIPE_MAIN_SHIFT_MAX_PX', 'H76_WIPE_STRETCH_MAX'):
    if tok not in w: fail('wipe refinement missing '+tok)
for bad in ('ghost2', 'rotation=', 'H71_WIPE_SECOND_GHOST_MAX_ALPHA'):
    if bad in w: fail('old dirty double-ghost/rotation leaked into H76 wipe '+bad)
if 'return _h76_fragment_draw_pre(row,painter,effect,progress)' not in w: fail('non-wipe/per-char exact delegate missing')
for tok,val,cmp in (('H76_WIPE_GHOST_MAX_ALPHA',0.085,'max veil'),('H76_WIPE_MAIN_SHIFT_MAX_PX',6.0,'main shift'),('H76_BLUR_RELEASE_VISIBLE_MIN_MS',760.0,'blur visible min'),('H76_BLUR_ABSOLUTE_EMERGENCY_MS',30000.0,'emergency'),('H76_BLUR_ORPHAN_RELEASE_TRIGGER',0.92,'orphan trigger'),('H76_BLUR_ORPHAN_HOLD_MAX',0.945,'orphan hold'),('H76_UI_PAGE_SETTLE_MS',165.0,'page motion'),('H76_UI_POPUP_ENTER_MS',180.0,'popup motion')):
    node=next((x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==tok for t in x.targets)),None)
    if node is None: fail('constant missing '+tok)
    got=float(ast.literal_eval(node.value))
    if abs(got-val)>1e-6: fail(f'{cmp} changed: {got}')
progress=fsrc('_h76_safe_blur_progress')
if "if float(getattr(row,'_h62_decay_release_mono'" not in progress or '_h76_blur_release_progress(row,now)' not in progress: fail('blur release owner missing')
for tok in ('action=hold-and-retry','_h69_optical_progress_floor','_h65_capacity_progress'):
    if tok not in progress: fail('blur progress fail-soft missing '+tok)
orphan=fsrc('_h76_schedule_orphan_history_blur_release')
for tok in ('_h68_exact_horizon_ms','H76_BLUR_ORPHAN_RELEASE_TRIGGER','QTimer.singleShot'):
    if tok not in orphan: fail('orphan history release scheduling missing '+tok)
promote=fsrc('_h76_promote_orphan_history_blur')
for tok in ('window.history_lines=[x for x in history if x is not row]','row.begin_fade()','window.fading_lines.append(row)','history-to-release'):
    if tok not in promote: fail('orphan history does not enter visible release '+tok)
if block.count('fading_lines.append(')!=1 or 'window.fading_lines.append(row)' not in promote:
    fail('H76 may append to fading only for the one orphan history-to-release promotion')
if 'H76_BLUR_ORPHAN_HOLD_MAX' not in progress or 'row._h62_decay_expired=False' not in progress:
    fail('orphan blur is not held below invisible retirement until release promotion')
upd=fsrc('_h76_fading_update')
for tok in ("if not _h66_is_blur_decay_row(row)", '_h76_blur_update_core(row)', 'action=keep-visible', 'draws<=0', '_render_force_full=True', 'draws>0', 'H76_BLUR_ABSOLUTE_EMERGENCY_MS'):
    if tok not in upd: fail('blur update recovery missing '+tok)
if 'H72_EXIT_HARD_MAX_MS' in upd: fail('blur still uses H72 generic 15s watchdog')
rel=fsrc('_h76_blur_release_progress')
for tok in ('H76_BLUR_RELEASE_VISIBLE_MIN_MS','H76_BLUR_RELEASE_VISIBLE_MAX_MS','_h62_decay_release_draw_count','_h69_optical_progress_floor'):
    if tok not in rel: fail('visible blur release missing '+tok)
act=fsrc('_h76_activate_runtime')
for tok in ('_h51_fragment_exit_draw=_h76_wipe_fragment_draw','_h62_decay_progress=_h76_safe_blur_progress','FadingLine.update=_h76_fading_update'):
    if tok not in act: fail('runtime hook missing '+tok)
uiact=fsrc('_h76_activate_ui')
for tok in ('ControlPanel._animate_current_tab=_h76_animate_current_tab','ControlPanel._h73_show_background_popup=_h76_show_background_popup','restrained page/flyout motion tokens'):
    if tok not in uiact: fail('H76 UI motion hook missing '+tok)
note=root/'EDITORIAL_POLISH_WIPE_BLUR_RECOVERY_H76_NOTE_20260905.md'
if not note.is_file(): fail('missing H76 note')
t=note.read_text(encoding='utf-8')
for tok in ('Per-character exit is intentionally unchanged','more than one display','palette + `背景`','15 s','30 s','no second ghost','history-to-release','165 ms','180 ms'):
    if tok not in t: fail('note incomplete '+tok)
print('EDITORIAL POLISH + WIPE REFINEMENT + BLUR RECOVERY H76 REPLAY: PASS')
print(' - H71 per-character exit stays unchanged; directional wipes use one faint short veil')
print(' - legacy exit-texture UI is hidden and target-screen control appears only with >1 display')
print(' - titlebar background shortcut is an icon+text utility instead of an ambiguous icon-only box')
print(' - blur exceptions hold/retry; orphan tail history is promoted into visible release instead of age-invisible retirement')
print(' - UI motion is tokenized: 165ms page settle and 180ms background flyout, with no decorative looping motion')
print(' - no player/provider/seek authority or new raster/thread dependency')
