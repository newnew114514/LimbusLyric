#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, random, re, sys, types, unicodedata, zlib
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_BILINGUAL_PRESET_RELEASE_COVER_H95F10F4_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ BILINGUAL PRESET + RELEASE COVER H95F10F4' in src,'H95F10F4 build tag missing')
need('# H95F10F4 bilingual preset parity + release-aware cover identity' in src,'H95F10F4 runtime marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
required=(
 '_h95f10f4_choose_qq_cover_row','_h95f10f4_choose_netease_cover_row','_h95f10f4_gsmtc_release_hint','_h95f10f4_request_art',
 '_h95f10f4_translation_base_font','_h95f10f4_entry_states','_h95f10f4_translation_shakes',
 '_h95f10f4_draw_active_translation','_h95f10f4_translation_exit_order','_h95f10f4_fragment_state',
 '_h95f10f4_draw_history_translation','_h95f10f4_schedule_translation_prewarm','_h95f10f4_activate')
for name in required: need(name in funcs,'H95F10F4 function missing: '+name)

# Release identity must be carried from media session, included in cache identity, and ambiguous
# same-track releases must be rejected rather than choosing the first search result.
for token in ("H95F10F4_ART_CACHE_SCHEMA = 'h95f10f4-art-release-v2'", '_h95f10f4_release_cache_key(key,album)', 'H95F10F4封面歧义拒绝'):
    need(token in src,'release-aware cover invariant missing: '+token)
release_src=ast.get_source_segment(src,funcs['_h95f10f4_gsmtc_release_hint']) or ''
for token in ('GlobalSystemMediaTransportControlsSessionManager.request_async','_choose_session','try_get_media_properties_async','album_title','_h95f2_title_score','_h95f2_strict_credit_match'):
    need(token in release_src,'cover-only release hint safety missing: '+token)
request_src=ast.get_source_segment(src,funcs['_h95f10f4_request_art']) or ''
for token in ('asyncio.run(_h95f10f4_gsmtc_release_hint','_h95f10f4_release_cache_key','_h95f10f4_fetch_qq_art','_h95f10f4_fetch_netease_art'):
    need(token in request_src,'cover request does not use release identity: '+token)
for token in ('_h95f10f4_art_request_evidence','evidence_improved','H95F10F4封面新证据提前重试','negative.pop(str(key),None)'):
    need(token in request_src,'cover negative-cache evidence retry missing: '+token)
need('H91_ART_NEGATIVE_RETRY_SEC = 28.0' in src,'true cover failures must keep bounded 28s backoff')
for token in ('_r9_2_fetch_netease_art','R9.2封面可信网易云ID直取','https://music.163.com/api/song/detail/',
              "globals()['_h95f10f4_fetch_netease_art'] = _r9_2_fetch_netease_art"):
    need(token in src,'R9.2 trusted NetEase cover direct-ID routing missing: '+token)
# Cover metadata must remain outside protected playback polling. RC11 also hash-locks these,
# but keep the ownership boundary explicit in the H95F10F4 replay.
need("update['media_album_title']" not in src,'cover patch leaked album metadata into protected transport polling')

# Execute QQ selector with two valid releases: without album evidence it must reject; with album
# evidence it must choose the matching release. This guards the old false "strict identity" claim.
sel_names=['_h95f10f4_norm_release','_h95f10f4_release_match','_h95f10f4_qq_album','_h95f10f4_choose_qq_cover_row']
nodes=[]
for name in sel_names:
    node=copy.deepcopy(funcs[name]); node.decorator_list=[]; nodes.append(node)
ns={'re':re,'random':random,'zlib':zlib,'_h95f8_unicodedata':unicodedata,
    '_h95f2_title_score':lambda wanted,actual:100 if str(wanted).casefold()==str(actual).casefold() else -1,
    '_h95f2_strict_credit_match':lambda wanted,actual:str(wanted).casefold()==str(actual).casefold(),
    '_h95f2_cover_duration_ok':lambda cand,wanted:abs(int(cand)-int(wanted))<=1000,
    '_h91_duration_score':lambda cand,wanted:20,
    '_artist_text':lambda row:', '.join(str(x.get('name') or '') for x in row.get('singer',[]) if isinstance(x,dict)),
    'write_error_log':lambda *a,**k:None}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<h95f10f4-cover>','exec'),ns)
rows=[
 {'songname':'Song','singer':[{'name':'Artist'}],'interval':200,'albummid':'ALB-A','albumname':'Album A'},
 {'songname':'Song','singer':[{'name':'Artist'}],'interval':200,'albummid':'ALB-B','albumname':'Album B'},
]
choose=ns['_h95f10f4_choose_qq_cover_row']
need(choose(rows,'Song','Artist',200000,'') is None,'ambiguous same-track releases still choose arbitrary QQ artwork')
hit=choose(rows,'Song','Artist',200000,'Album B')
need(isinstance(hit,dict) and hit.get('albummid')=='ALB-B','album evidence does not select matching QQ release')

# Translation typography must resolve from translation text/script, not inherit a Japanese/Latin
# primary result blindly. Active entrance/shake and history exits must use the mature user presets
# while keeping the cached-sprite hot path (no per-frame vector path reconstruction).
font_src=ast.get_source_segment(src,funcs['_h95f10f4_translation_base_font']) or ''
for token in ('_lyric_script_profile','_h51_script_font_enabled','_h51_script_fonts','_h51_size_range_enabled'):
    need(token in font_src,'translation typography preset missing: '+token)
active=ast.get_source_segment(src,funcs['_h95f10f4_draw_active_translation']) or ''
entry=ast.get_source_segment(src,funcs['_h95f10f4_entry_states']) or ''
shake=ast.get_source_segment(src,funcs['_h95f10f4_translation_shakes']) or ''
for token in ('_entrance_effect_for_text','_entrance_attack_profile','_entrance_ease','_entrance_motion'):
    need(token in entry,'translation entrance preset missing: '+token)
need('_advance_living_shake' in shake,'translation shake preset missing')
for token in ('_h95f10f4_translation_layout','_h95f7_sprite_for','_h95f7_draw_sprite'):
    need(token in active,'active translation cached-sprite/preset path missing: '+token)
for bad in ('_h95f6_main_index_for_secondary','char_index','QPainterPath','_h95f10f2_glyph_path'):
    need(bad not in active,'active translation regressed to primary-glyph/vector ownership: '+bad)

hist=ast.get_source_segment(src,funcs['_h95f10f4_draw_history_translation']) or ''
frag=ast.get_source_segment(src,funcs['_h95f10f4_fragment_state']) or ''
for effect in ("'per_char'","'wipe_ltr'","'wipe_rtl'","'blur_decay'"):
    need(effect in frag or effect in hist,'translation mature exit missing: '+effect)
for effect in ("'shrink'","'soft_drift'","'hop_drop'"):
    need(effect in (ast.get_source_segment(src,funcs.get('_h95f10f2_apply_history_group_transform')) or '') or effect in hist,'translation group exit missing: '+effect)
need('_h95f10f2_apply_history_group_transform' in hist,'translation does not reuse mature whole-row exit transform')
need('_h95f10f4_draw_sprite_xform' in hist and 'QPainterPath' not in hist,'translation history is not cached-sprite-only')
need('_h95f10f4_translation_exit_order' in frag,'translation fragment exit is not secondary-owned')
order_src=ast.get_source_segment(src,funcs['_h95f10f4_translation_exit_order']) or ''
need('_h95f10f4_translation_exit_order_cache' in order_src,'per-char translation exit order is recomputed in frame-hot path')

# F3's translation_result remains the fetch/alignment owner, but its runtime prewarm name must be
# redirected to F4 so the cache is primed with the translation's own resolved font.
prewarm=ast.get_source_segment(src,funcs['_h95f10f4_schedule_translation_prewarm']) or ''
for token in ('_h95f10f4_translation_prewarm_font','_h95f7_sprite_for','_render_pressure_level','QTimer.singleShot'):
    need(token in prewarm,'translation-aware bounded prewarm missing: '+token)
for bad in ('_schedule_song_fragment_atlas','threading.Thread','QPainterPath'):
    need(bad not in prewarm,'translation prewarm reintroduced expensive worker/vector path: '+bad)
_s=src.index('# H95F10F4 bilingual preset parity + release-aware cover identity')
block=src[_s:src.index('# H95F10F5 QQ auto-track rollback guard',_s)]
for token in ("globals()['_h95f7_draw_active_translation']=_h95f10f4_draw_active_translation", "globals()['_h95f7_draw_history_translation']=_h95f10f4_draw_history_translation", "globals()['_h95f10f3_schedule_translation_prewarm']=_h95f10f4_schedule_translation_prewarm", "globals()['_h91_request_art']=_h95f10f4_request_art"):
    need(token in block,'H95F10F4 final owner missing: '+token)
for bad in ('MediaSessionSync.position =','MediaSessionSync.seek =','LyricWindow.paintEvent=','FadingLine.draw=','parse_lrc ='):
    need(bad not in block,'H95F10F4 crossed protected timing/parser/paint authority: '+bad)
print('BILINGUAL PRESET + RELEASE COVER H95F10F4 REPLAY: PASS')
print('  release-aware cover identity + ambiguity rejection: PASS')
print('  translation script typography + entrance/shake/user exits: PASS')
print('  cached-sprite hotpath + translation-aware bounded prewarm: PASS')
print('  player timing/parser/primary paint authority untouched: PASS')
