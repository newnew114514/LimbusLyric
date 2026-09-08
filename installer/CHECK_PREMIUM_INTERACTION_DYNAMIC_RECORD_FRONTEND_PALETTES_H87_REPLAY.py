"""H87 premium interaction / dynamic record / frontend palette replay."""
import ast, math, sys, types
from pathlib import Path
sys.dont_write_bytecode=True
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_PREMIUM_INTERACTION_DYNAMIC_RECORD_FRONTEND_PALETTES_H87_REPLAY.py <root>')
root=Path(sys.argv[1]).resolve(); main=next(root.glob('LimbusLyric_*.py')); src=main.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def fn(name):
    node=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
    if node is None: raise SystemExit('H87 missing function '+name)
    return ast.get_source_segment(src,node) or '',node

ck('H87 build tag','+ PREMIUM INTERACTION + DYNAMIC RECORD + FRONTEND PALETTES H87' in src)
start=src.index('# H87 premium interaction + dynamic record + frontend palettes')
end=src.index('# H88 inspector workspace + cover fallback + smooth navigation',start)
block=src[start:end]
for bad in ('MediaSessionSync','LyricSearchEngine','FadingLine','_merge_uia_position','seek_session'):
    ck('presentation boundary excludes '+bad,bad not in block)
ck('workspace transition uses old and new frozen surfaces','class H87PageTransitionOverlay' in block and 'self._old = QPixmap(old_pix)' in block and 'self._new = QPixmap(new_pix)' in block)
cap,_=fn('_h87_capture_page_region')
ck('top navigation stays live',"getattr(panel, 'settings_main', None)" in cap and 'settings_shell' not in cap and 'top_nav' not in cap)
ck('single page animation owner','ControlPanel._animate_current_tab = _h87_animate_current_tab' in block and 'currentChanged.connect(lambda i, p=panel: _h87_on_page_changed' not in block)
ck('shared-axis transition is bounded','H87_PAGE_TRANSITION_MS = 218' in block and 'H87_PAGE_SHIFT_PX = 14' in block)
ck('record artwork patches existing hero ambient','H79HeroAmbient.paintEvent = _h87_ambient_paint' in block)
ck('record rotates only from playing state',"_h87_set_ambient_playing(ambient, str(state.get('status') or '').lower() == 'playing')" in block)
ck('record timer is bounded ~30fps','H87_RECORD_INTERVAL_MS = 33' in block)
ck('cover artwork uses disk cache','cover_art_cache_v1' in block and 'H87_ART_TTL_SEC = 90 * 24 * 60 * 60' in block)
ck('cover network work is daemonized',"threading.Thread(target=work, name='LimbusLyric-H87HeroCover', daemon=True).start()" in block)
ck('cover result becomes QPixmap only on UI poll','def _h87_poll_art_results' in block and 'QPixmap(path)' in block)
ck('frontend selector exposes studio and classic',"combo.addItem('Lyric Studio · 深林', 'studio')" in block and "combo.addItem('Classic · 玫瑰暗色', 'classic')" in block)
ck('frontend selector lives in Interface popup','def _h87_show_interface_popup' in block and "lay.insertWidget(2, section)" in block)
ck('frontend choice persists',"settings['h87_frontend_theme']" in block and "settings.get('h87_frontend_theme'" in block)
ck('hero progress reuses media snapshot','progress.set_progress(state.get(\'position_ms\'), state.get(\'duration_ms\'))' in block)
ck('no second transport poller','GlobalSystemMediaTransportControlsSessionManager' not in block and 'AsyncPlayerUiPositionReader' not in block)
ck('codex studio tail no late PyQt import',"from PyQt5.QtGui import QRadialGradient" not in src[start-6000:end] and "from PyQt5.QtWidgets import QSizePolicy" not in src[start-6000:end])

# Tiny behavior replay: frontend palette normalization and record motion stop/start.
_, theme_node=fn('_h87_frontend_theme')
_, trans_node=fn('_h87_cover_transition_active')
_, tick_node=fn('_h87_ambient_tick')
class Clock:
    value=10.0
    @classmethod
    def monotonic(cls): return cls.value
class Timer:
    def __init__(self): self.stopped=0
    def stop(self): self.stopped+=1
class Ambient:
    def __init__(self,playing):
        self._h87_last_tick=9.9; self._h87_angle=20.0; self._h87_playing=playing; self._h87_cover_started=0.0; self._h87_timer=Timer(); self.updated=0
    def update(self): self.updated+=1
ns={'H87_FRONTEND_DEFAULT':'studio','H87_COVER_FADE_MS':260,'H87_RECORD_DEG_PER_SEC':18.0,'time':Clock,'getattr':getattr,'bool':bool,'float':float,'max':max,'min':min}
exec(compile(ast.Module(body=[theme_node,trans_node,tick_node],type_ignores=[]),str(main),'exec'),ns)
ck('theme normalization behavior',ns['_h87_frontend_theme'](types.SimpleNamespace(_h87_frontend_theme='classic'))=='classic' and ns['_h87_frontend_theme'](types.SimpleNamespace(_h87_frontend_theme='other'))=='studio')
a=Ambient(True); ns['_h87_ambient_tick'](a); ck('playing record advances',1.7 < a._h87_angle-20.0 < 1.9 and a.updated==1 and a._h87_timer.stopped==0)
Clock.value=10.1; b=Ambient(False); b._h87_last_tick=10.0; ns['_h87_ambient_tick'](b); ck('paused record freezes and timer retires',abs(b._h87_angle-20.0)<1e-9 and b._h87_timer.stopped==1)

# Release regression: palette and H12 scale must compose instead of overwriting each other.
ck('palette/scale composition closure present', '# Release UI closure: palette + UI-scale composition' in src and "globals()['_h12_apply_scale'] = _r3_apply_scale_preserve_theme" in src and "globals()['_h87_apply_frontend_theme'] = _r3_apply_theme_preserve_scale" in src)
scale_src, scale_node = fn('_r3_scale_stylesheet')
scaled_ns={'re':__import__('re')}
exec(compile(ast.Module(body=[scale_node],type_ignores=[]),str(main),'exec'),scaled_ns)
css=scaled_ns['_r3_scale_stylesheet']('QWidget{font-size:10px;padding:4px;color:rose;}',1.5)
ck('palette/scale css preserves palette while scaling geometry','color:rose' in css and 'font-size: 15px' in css and 'padding: 6px' in css)
for name in ('_r3_apply_scaled_active_theme','_r3_apply_scale_preserve_theme','_r3_apply_theme_preserve_scale'):
    ck('palette/scale runtime helper '+name, any(isinstance(n,ast.FunctionDef) and n.name==name for n in tree.body))
ck('H87 note present',(root/'PREMIUM_INTERACTION_DYNAMIC_RECORD_FRONTEND_PALETTES_H87_NOTE_20260906.md').is_file())
print(f'H87 PREMIUM INTERACTION / DYNAMIC RECORD / FRONTEND PALETTES: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
