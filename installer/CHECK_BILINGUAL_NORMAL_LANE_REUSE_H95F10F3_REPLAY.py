#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys, types, math
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_BILINGUAL_NORMAL_LANE_REUSE_H95F10F3_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ BILINGUAL NORMAL-LANE REUSE H95F10F3' in src,'H95F10F3 build tag missing')
need('# H95F10F3 bilingual normal-lane reuse' in src,'H95F10F3 runtime marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name in (
    '_h95f10f3_schedule_translation_prewarm','_h95f10f3_translation_result',
    '_h95f10f3_translation_ordinary_state','_h95f10f3_draw_active_translation',
    '_h95f10f3_draw_history_translation','_h95f10f3_activate',
): need(name in funcs,'H95F10F3 function missing: '+name)

# 1) Active bilingual translation must be an independent ordinary-LRC lane. It may read
# the primary line/clock authority, but it must not mirror primary word/glyph reveal state.
active_src=ast.get_source_segment(src,funcs['_h95f10f3_draw_active_translation']) or ''
for bad in ('_h95f6_main_index_for_secondary','char_index','_h95f10f2_glyph_path','QPainterPath','_h95f6_primary_flow_state'):
    need(bad not in active_src,'active translation still mirrors/rebuilds primary glyph state: '+bad)
for token in ('_h95f10f3_translation_ordinary_state','_h95f7_sprite_for','_h95f7_draw_sprite'):
    need(token in active_src,'active translation does not use normal-lane sprite path: '+token)

# 2) Translation history owns its own exit order. A translated sentence can have a completely
# different length/script from the original without inheriting the original glyph permutation.
history_src=ast.get_source_segment(src,funcs['_h95f10f3_draw_history_translation']) or ''
for bad in ('_h95f6_main_index_for_secondary','_h95f10f2_primary_glyph_exit_state','_h95f10f2_glyph_path','QPainterPath'):
    need(bad not in history_src,'history translation still depends on primary/vector exit state: '+bad)
for token in ('_h95f6_exit_glyph_state(row,i,count)','_h95f7_sprite_for','_h95f7_draw_sprite'):
    need(token in history_src,'history translation is missing independent cached-sprite exit state: '+token)

# 3) Prewarm is bounded and never revives the expensive second full-song translated atlas.
prewarm_src=ast.get_source_segment(src,funcs['_h95f10f3_schedule_translation_prewarm']) or ''
for token in ('QTimer.singleShot','_h95f7_sprite_for','H95F10F3_TRANSLATION_PREWARM_MAX_CHARS','_render_pressure_level'):
    need(token in prewarm_src,'translation sprite prewarm safety missing: '+token)
for bad in ('_schedule_song_fragment_atlas','_h95f7_translation_atlas_shared','threading.Thread'):
    need(bad not in prewarm_src,'H95F10F3 reintroduced translated atlas/worker ownership: '+bad)

# 4) Execute the ordinary-lane state in isolation, specifically with line index ZERO. This
# guards the common `index or -1` bug and proves reveal cadence is derived from translation
# length + line timestamps rather than primary char_index/provider events.
node=copy.deepcopy(funcs['_h95f10f3_translation_ordinary_state']); node.decorator_list=[]
ns={'math':math}
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<h95f10f3-state>','exec'),ns)
state=ns['_h95f10f3_translation_ordinary_state']
class W:
    displayed_line_index=0
    lyric_timeline=[(0,'PRIMARY',(100,1)),(5000,'NEXT')]
    _last_position_ms=0
    char_index=999
    precise_tracking_enabled=True
    def _classic_span_profile(self,gap,n): return ('medium',1000.0)
    def _classic_visual_ms_per_char(self,gap,n): return 300.0
w=W(); v,pi,a=state(w,'abcdefghij')
need((v,pi)==(1,0) and 0.19<=a<=0.21,'line index 0 / first translated glyph reveal is broken')
w._last_position_ms=1500
v10,pi10,a10=state(w,'abcdefghij')
v20,pi20,a20=state(w,'abcdefghijklmnopqrst')
need(v10!=v20,'secondary reveal does not respond to translated text length')
need(v10<999 and v20<999,'secondary reveal leaked primary char_index authority')

# 5) Final owner must supersede H95F10F2 only at the bilingual presentation hooks. Timing,
# seek, parser, provider and primary paint ownership remain untouched.
start=src.index('# H95F10F3 bilingual normal-lane reuse')
end=src.index('# H95F10F4 bilingual preset parity + release-aware cover identity',start)
block=src[start:end]
for token in (
    "globals()['_h95f7_draw_active_translation']=_h95f10f3_draw_active_translation",
    "globals()['_h95f7_draw_history_translation']=_h95f10f3_draw_history_translation",
    "globals()['_h95f5_translation_result']=_h95f10f3_translation_result",
): need(token in block,'H95F10F3 final ownership missing: '+token)
for bad in ('MediaSessionSync.position =','MediaSessionSync.seek =','LyricWindow.paintEvent=','FadingLine.draw=','parse_lrc =','LyricSearchEngine.'):
    need(bad not in block,'H95F10F3 crossed protected authority: '+bad)
need(src.rfind("globals()['_h95f7_draw_active_translation']=_h95f10f3_draw_active_translation") > src.rfind("globals()['_h95f7_draw_active_translation']=_h95f10f2_draw_active_translation"),'H95F10F3 is not the final active-translation owner')
need(src.rfind("globals()['_h95f7_draw_history_translation']=_h95f10f3_draw_history_translation") > src.rfind("globals()['_h95f7_draw_history_translation']=_h95f10f2_draw_history_translation"),'H95F10F3 is not the final history-translation owner')
print('BILINGUAL NORMAL-LANE REUSE H95F10F3 REPLAY: PASS')
print('  primary precise/classic authority untouched; secondary reveal independent: PASS')
print('  secondary active/history paint uses mature cached sprites, no vector rebuild: PASS')
print('  translated atlas rebuild remains retired; bounded sprite prewarm only: PASS')
print('  line-index-zero and translated-length regression checks: PASS')
