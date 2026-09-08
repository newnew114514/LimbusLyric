#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, random, sys, types, zlib, math
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_STARTUP_ANCHOR_BILINGUAL_EXIT_FRAME_PACING_H95F10F2_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ STARTUP ANCHOR + BILINGUAL EXIT + FRAME PACING H95F10F2' in src,'H95F10F2 build tag missing')
need('# H95F10F2 startup anchor + bilingual exit ownership + frame pacing' in src,'H95F10F2 runtime marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name in ('_h95f10f2_qq_prelock_rail_anchor','_h95f10f2_translation_atlas_shared','_h95f10f2_primary_glyph_exit_state','_h95f10f2_draw_active_translation','_h95f10f2_draw_history_translation'):
    need(name in funcs,'H95F10F2 function missing: '+name)

# 1) Startup rail: a single transient value must never call the legacy one-sample commit.
node=copy.deepcopy(funcs['_h95f10f2_qq_prelock_rail_anchor']); node.decorator_list=[]
class FakeTime:
    now=1000.0
    @classmethod
    def monotonic(cls): return cls.now/1000.0
legacy=[]
def legacy_commit(self,ui,status): legacy.append((ui.get('position_ms'),status)); return True
ns={
    '_H95F10F2_QQ_PRELOCK_PRE':legacy_commit,'time':FakeTime,
    'H95F10F2_STARTUP_RAIL_MAX_BACKSTEP_MS':900.0,'H95F10F2_STARTUP_RAIL_CONFIRM_SAMPLES':3,
    'H95F10F2_STARTUP_RAIL_CONFIRM_SPAN_MS':260.0,'H95F10F2_STARTUP_RAIL_MAX_CLUSTER_MS':2600.0,
    'QQ_STARTUP_PRELOCK_RAIL_RELEASE_WINDOW_MS':5000.0,'QQ_STARTUP_PRELOCK_RAIL_MATCH_MIN_TOL_MS':1800.0,
    'QQ_STARTUP_PRELOCK_RAIL_MATCH_MAX_TOL_MS':12000.0,'QQ_STARTUP_PRELOCK_RAIL_MATCH_RATIO':0.05,
    'write_error_log':lambda *a,**k:None,
}
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<h95f10f2-anchor>','exec'),ns)
anchor=ns['_h95f10f2_qq_prelock_rail_anchor']
class S: pass
def state(gid,expected):
    s=S(); s._uia_duration_ms=248000; s._qq_gesture_release_mono=500.0; s._qq_gesture_id=gid; s._qq_gesture_expected_id=gid; s._qq_gesture_expected_ms=expected; s._h95f10f2_prelock_gid=0; return s
s=state(1,125130.0)
# Field-log pattern: one plausible ~123 s sample followed by the real 5 s stream.
for t,raw in ((1000.0,123000.0),(1200.0,5000.0),(1400.0,6000.0)):
    FakeTime.now=t; out=anchor(s,{'source':'qq-time-pair-validated','confidence':168,'position_ms':raw,'duration_ms':248000},'playing')
    need(out is None,'transient/reverse startup sample was committed')
need(not legacy,'legacy startup commit was called for transient field-log pattern')
# A genuine post-seek stream gets three coherent samples over a real span and then delegates.
s=state(2,50000.0); legacy.clear()
for t,raw in ((2000.0,49580.0),(2200.0,49780.0),(2400.0,49980.0)):
    FakeTime.now=t; out=anchor(s,{'source':'qq-time-pair-validated','confidence':168,'position_ms':raw,'duration_ms':248000},'playing')
need(len(legacy)==1 and out is True,'coherent 3-sample startup rail confirmation did not delegate exactly once')

# 2) Secondary full-song atlas is cache-only. Never schedule a second translated atlas.
node=copy.deepcopy(funcs['_h95f10f2_translation_atlas_shared']); node.decorator_list=[]; calls=[]
def pre_atlas(window,schedule=True): calls.append(bool(schedule)); return 'cache-hit'
ns={'_H95F10F2_TRANSLATION_ATLAS_PRE':pre_atlas}
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<h95f10f2-atlas>','exec'),ns)
need(ns['_h95f10f2_translation_atlas_shared'](object(),True)=='cache-hit','translation atlas cache hit was not reusable')
need(calls==[False],'translation atlas wrapper still schedules a second full-song atlas')

# 3) Historical H95F10F2 layer-local contract. H95F10F3 intentionally supersedes the
# final bilingual presentation owner; this section only proves the preserved H95F10F2 body
# remains reproducible for startup/frame-pacing regression archaeology.
history_src=ast.get_source_segment(src,funcs['_h95f10f2_draw_history_translation']) or ''
active_src=ast.get_source_segment(src,funcs['_h95f10f2_draw_active_translation']) or ''
for token in ('mi=_h95f6_main_index_for_secondary(i,slen,plen)','_h95f10f2_primary_glyph_exit_state(row,mi)'):
    need(token in history_src,'history translation is not mapped to primary glyph exit state: '+token)
need('_h95f6_exit_glyph_state(' not in history_src,'old translation-owned exit state is still used')
glyph_src=ast.get_source_segment(src,funcs.get('_h95f10f2_glyph_path')) or ''
need('_H95F10F2_TRANSLATION_PATH_CACHE' in glyph_src and 'owner._h95f10f2_translation_path_cache' not in glyph_src,'translation vector cache is still rebuilt per history row')
# The paint hot path must not construct/rasterize sprites synchronously.
for body,name in ((active_src,'active'),(history_src,'history')):
    need('_h95f7_sprite_for' not in body and '_hires_glyph_sprite' not in body,name+' translation still rasterizes sprites in paintEvent')
    need('_h95f10f2_glyph_path' in body,name+' translation is not using bounded cached vector glyphs')

# 4) Confirm per-char state depends only on primary row/index.  The helper itself cannot see the
# translated string length; changing secondary length therefore cannot invent a second exit order.
state_src=ast.get_source_segment(src,funcs['_h95f10f2_primary_glyph_exit_state']) or ''
for token in ('scatter[i]','_h70_seed_unit(row,i,17)','_h70_seed_unit(row,i,29)','_h70_seed_unit(row,i,43)'):
    need(token in state_src,'primary H71 per-char state component missing: '+token)
need('secondary_len' not in state_src and 'translation' not in state_src,'primary exit state still depends on translation lane geometry')
# H76 wipe uses primary geometric order and the reviewed clean veil constants.
for token in ('geom[i]', 'H76_WIPE_MAIN_SHIFT_MAX_PX', 'H76_WIPE_GHOST_MAX_ALPHA', 'H76_WIPE_STRETCH_MAX'):
    need(token in state_src,'primary H76 wipe state component missing: '+token)

# 5) Activation owns only the narrow presentation/startup hooks; no general seek/position override.
block=src[src.index('# H95F10F2 startup anchor + bilingual exit ownership + frame pacing'):src.index('if __name__ == "__main__":')]
for token in (
    "MediaSessionSync._qq_try_prelock_rail_validated_anchor=_h95f10f2_qq_prelock_rail_anchor",
    "globals()['_h95f7_translation_atlas_shared']=_h95f10f2_translation_atlas_shared",
    "globals()['_h95f7_draw_active_translation']=_h95f10f2_draw_active_translation",
    "globals()['_h95f7_draw_history_translation']=_h95f10f2_draw_history_translation",
): need(token in block,'H95F10F2 activation missing: '+token)
for bad in ('MediaSessionSync.position =','MediaSessionSync.seek =','LyricWindow._playback_position =','parse_lrc ='):
    need(bad not in block,'H95F10F2 crossed protected timing/parser authority: '+bad)
print('STARTUP ANCHOR + BILINGUAL EXIT + FRAME PACING H95F10F2 REPLAY: PASS')
print('  transient QQ startup rail sample rejected; coherent 3-sample seek accepted: PASS')
print('  historical H95F10F2 primary-mapped exit body preserved (final owner may supersede): PASS')
print('  translated full-song atlas scheduling + paint-time sprite rasterization retired: PASS')
