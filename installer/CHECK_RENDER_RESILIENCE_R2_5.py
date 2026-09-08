from pathlib import Path
import ast, sys
root=Path(sys.argv[1]).resolve()
main=next(root.glob('LimbusLyric_v1.8.9.133_*.py'))
src=main.read_text(encoding='utf-8')
tree=ast.parse(src)

def need(cond,msg):
    if not cond:
        print('RENDER RESILIENCE R2.5: FAIL '+msg)
        raise SystemExit(31)

def fn(name):
    return next((n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)

def seg(name):
    n=fn(name); lines=src.splitlines(); return '\n'.join(lines[n.lineno-1:n.end_lineno]) if n else ''

# Font coverage must be cached and invalidated on application font DB mutations.
fs=seg('_h51_font_supports_text')
need('_H51_FONT_SUPPORT_CACHE' in fs and '_H51_FONT_FAMILIES_CACHE' in fs,'H51 font coverage cache missing')
need('tuple(cps)' in fs and 'len(cps) >= 32' in fs,'representative codepoint cache key missing')
need(src.count("_h51_invalidate_font_support_cache('custom-font-") >= 3,'custom font load/import/reload invalidation incomplete')

# Held history must compile static geometry while preserving live shake each frame.
fr=seg('_draw_row_fragments')
for token in ('_r25_fragment_plan_key','transform_key','_device_space_staggered_wrap_adjust','self.char_shakes','drawPixmapFragments'):
    need(token in fr,'history fragment plan contract missing: '+token)
need(fr.find('cached is None') < fr.find('fm = QFontMetrics') < fr.rfind('self.char_shakes'), 'static geometry is not separated from frame-live shake')
need('conservative' in fr and 'shake_pad' in fr,'conservative dirty bounds missing')

# A pathological custom font may only fuse its style, not every subsequent font/style.
ss=seg('_schedule_song_fragment_atlas'); ins=seg('_install_song_fragment_atlas')
need('_song_fragment_atlas_fused_style_sig' in ss and "fused_sig == key[0]" in ss,'style-scoped atlas fuse gate missing')
need('r25-style-isolated-reset' in ss,'different-style fuse reset missing')
need('_song_fragment_atlas_fuse_until_mono' in ins and '120000.0' in ins,'bounded atlas fuse cooldown missing')
need('R2.5字幕渲染韧性优化激活' in src,'R2.5 activation diagnostic missing')

# Renderer patch must not alter historical runtime wrapper installation topology.
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

print('RENDER RESILIENCE R2.5: PASS')
print('  held-history static fragment geometry is compiled; live shake remains frame-live')
print('  custom-font coverage queries are bounded by an LRU + font-DB invalidation')
print('  song-atlas performance fuse is isolated to the expensive style signature')
print('  player/search/clock/frontend wrapper topology unchanged')
