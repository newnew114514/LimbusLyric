#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_RENDER_MODE_PRESET_PARITY_MATRIX_H95F10F15_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for n in ('_h95f10f10_profile_for_effect','_h95f10f10_resolved_visual_preset','_h95f10f12_live_line','_h95f10f12_track_line','_h95f10f12_lyric_facade','_h95f10f12_visual_timing_hints'):
    need(n in funcs,'missing '+n)
nodes=[]
for name in ('_h95f10f10_profile_for_effect','_h95f10f10_resolved_visual_preset'):
    node=copy.deepcopy(funcs[name]); node.decorator_list=[]; nodes.append(node)
ns={'H70_SPEED_DEFAULT':100,'H95F6_TRANSLATION_SCALE_DEFAULT':82,'H95F5_TRANSLATION_GAP_DEFAULT':12,'AUDIO_EMPHASIS_DEFAULT_MAX_SCALE_PCT':112,'AUDIO_EMPHASIS_TRIGGER_DEFAULT_PCT':28,'AUDIO_EMPHASIS_FULL_DEFAULT_PCT':72}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<preset-matrix>','exec'),ns)
class W:
    exit_effect='blur_decay'; entrance_effect='rise'; western_entrance_effect='slide'
    _h70_exit_profiles={'blur_decay':{'speed':137,'flavor':64}}
    _h95f5_translation_scale_pct=79; _h95f5_translation_gap_px=17
    shake_intensity=2.5; shake_speed=111
    audio_emphasis_enabled=True; audio_emphasis_max_scale_pct=118
    audio_emphasis_trigger_threshold=.31; audio_emphasis_full_threshold=.77
    perspective_enabled=True; persp_x_strength=.012; persp_y_strength=-.009
    horizontal_wrap=True; spacing=1.75
plan={'primary_style':('font','main'),'translation_style':('font','trans')}
keys=('entrance_effect','western_entrance_effect','exit_effect','exit_speed','exit_flavor','shake_intensity','shake_speed_ms','audio_enabled','audio_scale_pct','audio_trigger','audio_full','perspective_enabled','persp_x','persp_y','horizontal_wrap','spacing')
base=None
for mode in ('precise','classic','trans_only','bilingual'):
    w=W(); w._h95f5_bilingual_mode=mode
    out=ns['_h95f10f10_resolved_visual_preset'](w,dict(plan))
    cur=tuple(out[k] for k in keys)
    if base is None: base=cur
    need(cur==base,f'user preset drifted by render mode: {mode}')
need(base[0]=='rise' and base[2]=='blur_decay' and base[3]==137 and base[4]==64,'selected entrance/exit profile not preserved')

# Main precision changes main timing only; translation remains line-timed in the common facade.
nodes=[]
for name in ('_h95f10f12_track_line','_h95f10f12_live_line','_h95f10f12_lyric_facade','_h95f10f12_visual_timing_hints'):
    node=copy.deepcopy(funcs[name]); node.decorator_list=[]; nodes.append(node)
ns2={'H95F10F12_SCHEMA':1}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<timing-matrix>','exec'),ns2)
class L: pass
w=L(); w.lyric_timeline=[(1000,'原文',[('x',)]),(3000,'next',None)]
w._h95_unified_track={'source':'酷狗','identity':'song|artist','lines':[{'text':'原文','translation':'译文','words':[{'start_ms':1000,'end_ms':1800},{'start_ms':1800,'end_ms':2600}],'end_ms':3000},{'text':'next','translation':'下一句','words':[],'end_ms':5000}]}
f=ns2['_h95f10f12_lyric_facade'](w,0,{'idx':0,'primary_text':'原文','translation':'译文'})
t=ns2['_h95f10f12_visual_timing_hints'](w,0,f)
need(f['quality']==3 and f['main_timing']=='word','precise main facade did not keep word timing')
need(f['translation_timing']=='line' and t['translation_timing']=='line','translation was remapped onto source word timing')
need(t['content_end_ms']==2600 and t['handoff_ms']==3000,'content/handoff timing contract drifted')

# The final bilingual renderer must keep mature preset owners rather than a private effect list.
f7=ast.get_source_segment(src,funcs.get('_h95f10f7_draw_active_translation')) or ''
for token in ('_h95f10f7_ordinary_snapshot','_h95f10f4_translation_shakes','_h95f10f7_translation_audio_scales'):
    need(token in f7,'bilingual active lane lost mature preset integration '+token)
print('RENDER MODE PRESET PARITY MATRIX H95F10F15 REPLAY: PASS')
print('  precise/classic/trans-only/bilingual resolve the same selected user visual preset: PASS')
print('  precise main remains word-timed while translation stays ordinary line-timed: PASS')
print('  entrance/exit speed+flavor/shake/audio/perspective/wrap do not drift by mode: PASS')
