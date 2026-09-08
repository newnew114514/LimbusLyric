#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, re, html, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_FROST_MATERIAL_COVER_IDENTITY_HEADER_COLLISION_H95F2_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
marker='# H95F2 frost material + cover identity + Hero collision closure'
need(marker in src,'H95F2 marker missing')
need('+ FROST MATERIAL + COVER IDENTITY + HEADER COLLISION H95F2' in src,'H95F2 build tag missing')
next_marker='# H95F3 preview fit + classic compact frontend'
need(next_marker in src,'H95F3 boundary marker missing')
block=src[src.index(marker):src.index(next_marker,src.index(marker))]
for bad in ('MediaSessionSync.','LyricWindow._playback_position =','parse_lrc =','LyricSearchEngine.search ='):
    need(bad not in block,'H95F2 crossed timing/lyric authority: '+bad)

wanted={'_h95f2_artist_tokens','_h95f2_strict_credit_match','_h95f2_compact_badge_text'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted]
need({n.name for n in nodes}==wanted,'H95F2 pure helpers missing')
def clean(v): return re.sub(r'[\s\-–—－_·•\.\(\)（）\[\]【】]+','',str(v or '').lower().strip())
ns={'re':re,'html':html,'_clean_name':clean,'H95F1_HERO_DEFAULT_H':176}
# execute in dependency order
for name in ('_h95f2_artist_tokens','_h95f2_strict_credit_match','_h95f2_compact_badge_text'):
    node=next(n for n in nodes if n.name==name); exec(compile(ast.Module(body=[node],type_ignores=[]),'<h95f2-pure>','exec'),ns)
match=ns['_h95f2_strict_credit_match']
need(match('ぽわぽわP/鏡音リン','ぽわぽわP/鏡音リン'),'exact multi-credit rejected')
need(match('ぽわぽわP/鏡音リン','ぽわぽわP'),'primary-credit-only should stay valid')
need(not match('ぽわぽわP/鏡音リン','椎名もた/鏡音リン'),'one shared vocalist must not authorize a different primary credit')
need(not match('Producer A/Vocal B','Producer C/Vocal B'),'generic collaborator overlap accepted wrong release')
need(match('Producer A/Vocal B','Producer A'),'primary release credit not retained')
# Execute real H95F2 row selectors against the reported 少女A ambiguity, not just source text.
selector_names={'_h95f2_title_score','_h95f2_cover_duration_ok','_h95f2_choose_qq_cover_row','_h95f2_choose_netease_cover_row'}
selector_nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in selector_names]
need({n.name for n in selector_nodes}==selector_names,'H95F2 artwork selector helpers missing')
def norm(v): return clean(v)
def song_variants(v):
    raw=str(v or '')
    return [raw,'少女A'] if '少女A' in raw else [raw]
def artist_text(row):
    return '/'.join(str(x.get('name') or '') for x in row.get('singer',[]) if isinstance(x,dict))
def duration_score(c,e):
    if not c or not e: return 0
    d=abs(int(c)-int(e)); return 30 if d<=1500 else 10 if d<=4200 else -120
selns=dict(ns)
selns.update({'_h91_norm':norm,'_h91_song_variants':song_variants,'_artist_text':artist_text,'_h91_duration_score':duration_score,'_h16_cover_pic_url':lambda row: str(((row.get('album') or {}).get('picUrl')) or row.get('picUrl') or '')})
for name in ('_h95f2_title_score','_h95f2_cover_duration_ok','_h95f2_choose_qq_cover_row','_h95f2_choose_netease_cover_row'):
    node=next(n for n in selector_nodes if n.name==name); exec(compile(ast.Module(body=[node],type_ignores=[]),'<h95f2-selector>','exec'),selns)
qq_rows=[
 {'songname':'少女A','songmid':'wrong','albummid':'wrongalbum','interval':242,'singer':[{'name':'椎名もた'},{'name':'鏡音リン'}]},
 {'songname':'少女A','songmid':'right','albummid':'rightalbum','interval':242,'singer':[{'name':'ぽわぽわP'},{'name':'鏡音リン'}]},
]
qq_hit=selns['_h95f2_choose_qq_cover_row'](qq_rows,'【鏡音リン】少女A【椎名もた】','ぽわぽわP/鏡音リン',242000)
need(isinstance(qq_hit,dict) and qq_hit.get('songmid')=='right','QQ cover selector authorized wrong credit/release')
qq_wrong_only=selns['_h95f2_choose_qq_cover_row'](qq_rows[:1],'【鏡音リン】少女A【椎名もた】','ぽわぽわP/鏡音リン',242000)
need(qq_wrong_only is None,'QQ cover selector should prefer no art over wrong primary credit')
netease_rows=[
 {'id':1,'name':'少女A','dt':242000,'ar':[{'name':'椎名もた'},{'name':'鏡音リン'}],'album':{'picUrl':'https://wrong'}},
 {'id':2,'name':'少女A','dt':242000,'ar':[{'name':'ぽわぽわP'},{'name':'鏡音リン'}],'album':{'picUrl':'https://right'}},
]
ne_hit=selns['_h95f2_choose_netease_cover_row'](netease_rows,'【鏡音リン】少女A【椎名もた】','ぽわぽわP/鏡音リン',242000,'')
need(isinstance(ne_hit,dict) and ne_hit.get('id')==2,'NetEase cover selector authorized wrong credit/release')
compact=ns['_h95f2_compact_badge_text']
need(compact('正在同步 · 暂停',70)=='暂停','mini badge not compact enough')
need(compact('正在同步 · 暂停',100)=='同步 · 暂停','tight badge not compacted')
need(compact('正在同步 · 暂停',176)=='正在同步 · 暂停','roomy badge should retain full status')

need('p.drawPixmap(0,0,base)' in block,'frost material does not preserve source structure')
need('drawTiledPixmap' in block and '_h95f2_grain_tile' in block,'frost material lacks micro-grain')
need("globals()['_h95f1_frost_pixmap']=_h95f2_frost_pixmap" in block,'H95F2 frost renderer not installed')
need('badge.mapTo(hero,QPoint(0,0))' in block and 'legend.intersects(brect)' in block,'LISTENING ROOM collision guard missing')
need("badge.setMaximumWidth" in block,'sync badge responsive width guard missing')
need("H95F2_ART_CACHE_SCHEMA = 'h95f2-art-identity-v1'" in block,'art cache schema salt missing')
need("globals()['_h87_art_file_for_key']=_h95f2_art_file_for_key" in block,'new artwork cache namespace not active')
need("globals()['_h91_fetch_qq_art']=_h95f2_fetch_qq_art" in block and "globals()['_h91_fetch_netease_art']=_h95f2_fetch_netease_art" in block,'strict shared artwork fetch not installed')
need("settings['h95f2_cover_identity_migrated']=True" in block,'legacy cover/color evidence migration guard missing')
print('FROST MATERIAL + COVER IDENTITY + HEADER COLLISION H95F2 REPLAY: PASS')
print('  multi-credit cover identity / same-vocalist false-positive guard: PASS')
print('  frosted material = restrained diffusion + source structure + micro-grain: PASS')
print('  sync badge / LISTENING ROOM collision + compact status copy: PASS')
