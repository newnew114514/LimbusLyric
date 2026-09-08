from pathlib import Path
import sys,re
if len(sys.argv)<2: raise SystemExit('usage: CHECK_LIVE_LYRIC_SMOOTH_TRANSITION_H79_REPLAY.py <main.py>')
main=Path(sys.argv[1]); src=main.read_text(encoding='utf-8'); root=main.parent
def fail(m): raise SystemExit('H79 FAIL: '+m)
def need(tok,label=None):
    if tok not in src: fail('missing '+(label or tok))
need('+ LIVE LYRIC SHELL + SMOOTH SNAPSHOT TRANSITION H79','build tag')
need('# H79 live lyric shell + smooth snapshot transition','marker')
if not (src.rindex("if '_h78_activate_ui' in globals():") < src.rindex("if '_h79_activate_ui' in globals():")): fail('H79 must activate after H78')
block=src[src.index('# H79 live lyric shell + smooth snapshot transition'):]
if '# H80 stable studio stage + micro-motion hierarchy' in block:
    block=block[:block.index('# H80 stable studio stage + micro-motion hierarchy')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync','LyricSearchEngine','FadingLine','fading_lines','begin_fade','threading.Thread','requests.','win32gui','uiautomation','save_all_config(','load_all_config('):
    if bad in block: fail('crossed presentation boundary: '+bad)
# Product semantics: this destination is subtitle styling, not application appearance.
for tok in ("panel.main_tabs.setTabText(1,'字幕')", "buttons[1].setText('字幕')", "meta[1]=('字幕','实时预览、字体、排版、布局、色彩与光效')", "labels=('PLAYBACK','LYRICS','MOTION','SYSTEM','SONG OVERRIDE')"):
    if tok not in block: fail('subtitle naming closure missing '+tok)
# Dense pages must not receive a page-wide QGraphicsOpacityEffect anymore.
for bad in ("QGraphicsOpacityEffect(page)", "QGraphicsOpacityEffect(header)", "QPropertyAnimation(effect, b'opacity'"):
    if bad in block: fail('dense page opacity animation returned: '+bad)
for tok in ('class H79PageTransitionOverlay(QWidget)', 'panel.grab(rect)', 'H79_PAGE_RISE_PX = 10', '_h79_ui_frame_interval', 'Qt.PreciseTimer', 'self._timer.setInterval(_h79_ui_frame_interval(panel))'):
    if tok not in block: fail('snapshot transition / refresh-aware timer missing '+tok)
m=re.search(r'^H79_PAGE_TRANSITION_MS\s*=\s*(\d+)',block,re.M)
if not m or not (130 <= int(m.group(1)) <= 190): fail('page transition must stay quick, 130..190ms')
# Existing 24ms/~42fps H74 preview must be upgraded by outer presentation only.
for tok in ("stage=getattr(panel,'h74_motion_preview',None)", "timer.setInterval(_h79_ui_frame_interval(panel))", 'H79_UI_MAX_REFRESH_HZ = 120.0'):
    if tok not in block: fail('preview refresh closure missing '+tok)
# LimbusLyric-specific content identity: actual current line/style feeds Hero without new acquisition.
for tok in ("raw=str(getattr(panel.lyric_window,'full_text','')", "QFont(getattr(panel.lyric_window,'font',QFont()))", "getattr(panel.lyric_window,'text_color'", "class H79HeroAmbient(QFrame)", "sample.setObjectName('h79LiveLyric')"):
    if tok not in block: fail('live lyric shell missing '+tok)
for bad in ("settings['h79", "setdefault('settings')", 'QImage.fromData', 'requests.get', 'requests.post'):
    if bad in block: fail('H79 must not create config/network ownership: '+bad)
note=root/'LIVE_LYRIC_SMOOTH_TRANSITION_H79_NOTE_20260905.md'
if not note.is_file(): fail('missing H79 note')
print('LIVE LYRIC SHELL + SMOOTH SNAPSHOT TRANSITION H79 REPLAY: PASS')
