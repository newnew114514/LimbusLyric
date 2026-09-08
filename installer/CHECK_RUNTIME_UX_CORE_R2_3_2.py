from pathlib import Path
import ast, re, sys
root=Path(sys.argv[1]).resolve()
main=next(root.glob('LimbusLyric_v1.8.9.133_*.py'))
src=main.read_text(encoding='utf-8')
ast.parse(src)

def need(c,m):
    if not c:
        print('RUNTIME UX CORE R2.3.2: FAIL '+m)
        raise SystemExit(31)

# Preview entrance must be attached by ownership, never fixed header indices.
block=src[src.index('def _r23_install_title_preview_button'):src.index('def _r23_frontend_polish')]
need('child.widget() is title' in block,'preview owner scan missing')
need('itemAt(0).layout()' not in block,'preview installer regressed to item 0 assumption')
need("setObjectName('r23TitlePreviewButton')" in block,'preview title button missing')

# Open preview is framed and folded preview costs zero height.
need('QFrame#h80StudioStageHost {' in src[src.index('R23_QSS'):src.index('class R23RegionMiniPreview')], 'preview host frame QSS missing')
need('border:1px solid rgba(209,164,171,82)' in src,'preview frame not visible enough')
need('host.setMinimumHeight(0); host.setMaximumHeight(0); host.hide()' in src,'folded preview does not release layout height')

# One preview state owner: reuse H89 persisted setting. R2.3 key may only be read for migration.
need("settings['h89_preview_open'] = bool(opened)" in src,'H89 preview state not persisted canonically')
need("settings.pop('r23_title_preview_open', None)" in src,'old R2.3 preview state not migrated away')
need("panel._h89_preview_open = opened" in src,'title button does not drive H89 owner state')

# Preset controls move, and the now-empty standalone card is physically removed so section rail cannot resurrect it.
merge=src[src.index('def _r23_merge_preset_into_font'):src.index('def _r23_region_ui')]
need('page.layout().removeWidget(preset)' in merge,'retired preset card still remains in page layout')
need("preset.setProperty('h75SearchIgnore', True)" in merge,'retired preset card not search-hidden')

# Region preview remains horizontal/compact, not a hidden full-height reservation.
need('R23_REGION_MINI_W = 118' in src and 'R23_REGION_MINI_H = 48' in src,'compact region dimensions changed')
need('card.layout().removeWidget(old)' in src,'old large region preview not physically removed')

# R2.3 added two core APIs. They are intentionally staged APIs, not active runtime claims.
# Main module must not import helpers it does not consume.
need('_core_active_line_window' not in src,'unused active_line_window main-module import remains')
need('_core_build_line_render_hints' not in src,'unused build_line_render_hints main-module import remains')
need('MediaSessionSync.sampled_snapshot = _s2_playback_sampled_contract' in src,'sampled snapshot contract disappeared')
need('MediaSessionSync.capability_snapshot = _s2_capability_contract' in src,'capability snapshot contract disappeared')

# Historical topology is still untouched.
tree=ast.parse(src)
def count_attr_assign(owner,attr):
    n=0
    for node in ast.walk(tree):
        if not isinstance(node,ast.Assign): continue
        for t in node.targets:
            if isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id==owner and t.attr==attr:
                n+=1
    return n
for owner,attr,count in (
    ('ControlPanel','__init__',54),('LyricWindow','paintEvent',10),('FadingLine','draw',17),
    ('LyricWindow','_make_history_line',18),('LyricSearchEngine','search',5),
    ('MediaSessionSync','bind_track',6),('MediaSessionSync','snapshot',4)):
    need(count_attr_assign(owner,attr)==count,f'{owner}.{attr} topology changed')

print('RUNTIME UX CORE R2.3.2: PASS')
print('  preview has visible frame and title-owner attachment')
print('  preview state is single-owner H89 with R2.3 migration fallback')
print('  retired preset card is removed from section navigation layout')
print('  staged core APIs are not misrepresented as active consumers')
