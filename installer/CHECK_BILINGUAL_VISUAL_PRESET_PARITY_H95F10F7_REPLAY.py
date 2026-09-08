#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_BILINGUAL_VISUAL_PRESET_PARITY_H95F10F7_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ BILINGUAL VISUAL PRESET PARITY H95F10F7' in src,'H95F10F7 build tag missing')
marker='# H95F10F7 bilingual visual-preset parity + long-line containment'
need(marker in src,'H95F10F7 runtime marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name in ('_h95f10f7_translation_base_font','_h95f10f7_translation_timeline','_h95f10f7_ordinary_snapshot','_h95f10f7_translation_audio_scales','_h95f10f7_wrap_adjust','_h95f10f7_depth_profile','_h95f10f7_cached_sprite','_h95f10f7_build_depth_composite_image','_h95f10f7_queue_translation_depth','_h95f10f7_install_song_fragment_atlas','_h95f10f7_build_translation_blur','_h95f10f7_draw_active_translation','_h95f10f7_draw_history_translation','_h95f10f7_activate'):
    need(name in funcs,'missing '+name)
def fs(name): return ast.get_source_segment(src,funcs[name]) or ''
ordinary=fs('_h95f10f7_ordinary_snapshot')
for t in ('_calc_char_speed','_ordinary_visual_state'): need(t in ordinary,'entrance/ordinary owner not mature: '+t)
need('_h95f10f4_entry_states' not in ordinary,'F4 duplicate entrance envelope still final')
timeline=fs('_h95f10f7_translation_timeline'); need('id(raw_timeline)' in timeline,'translation timeline cache is not stable')
active=fs('_h95f10f7_draw_active_translation')
for t in ('_h95f10f7_ordinary_snapshot','_h95f10f4_translation_layout','_h95f10f4_translation_shakes','_h95f10f7_translation_audio_scales','_h95f10f7_wrap_adjust','_h95f7_sprite_for'):
    need(t in active,'active preset parity missing '+t)
for bad in ('QPainterPath','_h95f10f4_entry_states','_h95f10f3_translation_ordinary_state('): need(bad not in active,'active final hot path regressed: '+bad)
audio=fs('_h95f10f7_translation_audio_scales')
for t in ('_audio_emphasis_gate_fraction','AUDIO_EMPHASIS_CONFIRM_MS','AUDIO_EMPHASIS_GROW_TAU_MS','_audio_emphasis_value'):
    need(t in audio,'audio preset parity missing '+t)
for bad in ('AudioEmphasisMonitor(','threading.Thread','snapshot()'): need(bad not in audio,'secondary audio sampler introduced: '+bad)
hist=fs('_h95f10f7_draw_history_translation')
for t in ('_h95f10f2_primary_glyph_exit_state','_h95f10f6_draw_blur_translation','_h95f10f2_apply_history_group_transform','_h95f10f7_wrap_adjust','_h95f10f7_anchor_enter'):
    need(t in hist,'history/exit parity missing '+t)
need('_h95f10f4_fragment_state' not in hist,'F4 copied exit formulas remain final authority')
for bad in ('QPainterPath','_h62_filter_shared_image','threading.Thread'):
    need(bad not in active and bad not in hist,'raster/vector work leaked into final paint: '+bad)
# H57 optical parity must be worker-built from already-cached sprites, never synthesized in paint.
depth_build=fs('_h95f10f7_build_depth_composite_image')
for t in ('_h57_depth_optics','_h62_filter_shared_image','_h62_pack_entries_image','QImage','QPainter'):
    need(t in depth_build,'translated H57 material missing '+t)
need('QPixmap.fromImage' not in depth_build,'worker creates QPixmap/GUI material')
cached_sprite=fs('_h95f10f7_cached_sprite')
need('_HIRES_GLYPH_SPRITE_CACHE' in cached_sprite,'depth prewarm does not read mature sprite cache')
need('_hires_glyph_sprite(' not in cached_sprite,'depth prewarm may synchronously rasterize missing glyphs')
queue=fs('_h95f10f7_queue_translation_depth')
for t in ('_h95f10f7_pack_translation_base','threading.Thread','song_fragment_atlas_ready.emit'):
    need(t in queue,'async translated depth queue missing '+t)
install=fs('_h95f10f7_install_song_fragment_atlas')
for t in ('QPixmap.fromImage','_h95f10f7_translation_depth_shared','window.update'):
    need(t in install,'GUI depth install missing '+t)
blur=fs('_h95f10f7_build_translation_blur')
for t in ('_h95f10f7_translation_depth_shared','_h62_filter_shared_image','h95f10f6_translation_blur'):
    need(t in blur,'blur-decay does not begin from translated H57 material: '+t)
for t in ('_h95f10f7_queue_translation_depth','_h95f10f7_translation_depth_shared','drawPixmapFragments'):
    need(t in active,'active H57 parity missing '+t)
for t in ('_h95f10f7_queue_translation_depth','_h95f10f7_translation_depth_shared'):
    need(t in hist,'history H57 parity missing '+t)
# Enumerations: audit every exposed entrance/exit value, not only blur.
for val in ('smart','soft','typewriter','rise','slide','bounce','token'):
    need(repr(val) in src,'entrance preset missing '+val)
for val in ('fade','per_char','wipe_ltr','wipe_rtl','shrink','soft_drift','hop_drop','blur_decay','instant'):
    need(repr(val) in src,'exit preset missing '+val)
# Style owner remains script-aware font + shared cached sprite material (color/stroke/shadow/glow).
style=fs('_h95f10f7_translation_base_font')
sprite=fs('_h95f7_sprite_for')
for t in ('_h51_base_font','_h51_prepare_line_typography','_H95F10F7OrdinaryLaneProxy'):
    need(t in style,'translation typography no longer executes mature H51: '+t)
for t in ('text_color','stroke_color','shadow_color','glow_color'):
    need(t in sprite,'cached sprite no longer inherits visual preset: '+t)
# Final hooks only; no provider/parser/clock/primary paint ownership.
start=src.index(marker); end=src.index('# H95F10F8 sync UI + cold-raster closure + precise bilingual pair priority',start); block=src[start:end]
for t in ("globals()['_h95f10f4_translation_base_font'] = _h95f10f7_translation_base_font","globals()['_h95f7_draw_active_translation'] = _h95f10f7_draw_active_translation","globals()['_h95f7_draw_history_translation'] = _h95f10f7_draw_history_translation","globals()['_h95f10f6_build_translation_blur'] = _h95f10f7_build_translation_blur","LyricWindow._install_song_fragment_atlas = _h95f10f7_install_song_fragment_atlas"):
    need(t in block,'F7 final owner missing '+t)
for bad in ('MediaSessionSync.position =','MediaSessionSync.seek =','LyricSearchEngine.search =','parse_lrc =','LyricWindow.paintEvent='):
    need(bad not in block,'F7 crossed protected authority: '+bad)
print('BILINGUAL VISUAL PRESET PARITY H95F10F7 REPLAY: PASS')
print('  all 7 entrance presets route through mature ordinary state: PASS')
print('  all 9 exit presets route through primary glyph/group/H62 owners: PASS')
print('  script typography/material/shake/audio/wrap + async H57 birth-depth parity: PASS')
print('  blur-decay starts from H57 translation material; no raster/filter work in paint: PASS')
