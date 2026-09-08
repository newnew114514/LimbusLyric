from pathlib import Path
import sys,re
if len(sys.argv)<2: raise SystemExit('usage: CHECK_STABLE_STUDIO_MICRO_MOTION_H80_REPLAY.py <main.py>')
main=Path(sys.argv[1]); src=main.read_text(encoding='utf-8'); root=main.parent
def fail(m): raise SystemExit('H80 FAIL: '+m)
def need(tok,label=None):
    if tok not in src: fail('missing '+(label or tok))
need('+ STABLE STUDIO STAGE + MICRO MOTION H80','build tag')
need('# H80 stable studio stage + micro-motion hierarchy','marker')
if not (src.rindex("if '_h79_activate_ui' in globals():") < src.rindex("if '_h80_activate_ui' in globals():")): fail('H80 must activate after H79')
block=src[src.index('# H80 stable studio stage + micro-motion hierarchy'):]
if '# H81 lyric identity firewall / cross-version cache quarantine' in block:
    block=block[:block.index('# H81 lyric identity firewall / cross-version cache quarantine')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync','LyricSearchEngine','FadingLine','fading_lines','begin_fade','threading.Thread','requests.','win32gui','uiautomation','save_all_config(','load_all_config('):
    if bad in block: fail('crossed presentation boundary: '+bad)
# H79 whole-page snapshot transition is retired rather than tuned again.
for bad in ('H79PageTransitionOverlay(', 'panel.grab(', "QGraphicsOpacityEffect(page)", "QGraphicsOpacityEffect(header)"):
    if bad in block: fail('whole-page transition returned: '+bad)
for tok in (
    'def _h80_install_studio_stage(panel):',
    "appearance_card = appearance_stage.parentWidget()",
    "motion_card = motion_stage.parentWidget()",
    "style_page.layout().removeWidget(appearance_card)",
    "motion_page.layout().removeWidget(motion_card)",
    "host.setObjectName('h80StudioStageHost')",
    "shell_layout.insertWidget(max(0, insert_at), host)",
    "panel.h80_appearance_stage_card = appearance_card",
    "panel.h80_motion_stage_card = motion_card",
):
    if tok not in block: fail('stable stage closure missing '+tok)
# Micro-motion is semantic-landmark only: workspace title + first section title.
for tok in (
    'H80_TITLE_REVEAL_MS = 145', 'H80_SECTION_REVEAL_MS = 125', 'H80_REVEAL_DY_PX = 5',
    'def _h80_first_visible_section_label(panel, index):',
    "_h80_reveal_label(panel, getattr(panel, 'workspace_title', None)",
    "_h80_reveal_label(panel, first, 'section-title'",
    "QPropertyAnimation(label, b'pos', panel)",
    "QGraphicsOpacityEffect(label)",
):
    if tok not in block: fail('landmark micro-motion missing '+tok)
# No row/card animation loop or persistent high-frequency UI clock.
for bad in ("for row in panel.findChildren", "for card in panel.findChildren(QFrame):\n            _h80_reveal_label", 'setInterval(8)', 'setInterval(16)'):
    if bad in block:
        fail('decorative/persistent animation pattern returned: '+bad)
# Existing H74 stage is reused, not recreated or duplicated.
if 'H74PreviewStage(' in block: fail('H80 must reuse mature H74 preview objects, not create another preview stage')
# Subtitle product naming from H79 must remain the destination.
if "panel.main_tabs.setTabText(1,'字幕')" not in src: fail('subtitle destination naming lost')
note=root/'STABLE_STUDIO_MICRO_MOTION_H80_NOTE_20260905.md'
if not note.is_file(): fail('missing H80 note')
print('STABLE STUDIO STAGE + LANDMARK MICRO MOTION H80 REPLAY: PASS')
