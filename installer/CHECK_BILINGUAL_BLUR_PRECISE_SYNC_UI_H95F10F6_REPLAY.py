#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys, threading, types
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_BILINGUAL_BLUR_PRECISE_SYNC_UI_H95F10F6_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ BILINGUAL BLUR + PRECISE CACHE + SYNC UI H95F10F6' in src,'H95F10F6 build tag missing')
marker='# H95F10F6 bilingual optical blur parity + precise recovery + sync UI cleanup'
need(marker in src,'H95F10F6 runtime marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
required=(
 '_h95f10f6_precise_cache_row_is_soft','_h95f10f6_purge_soft_precise_cache','_h95f10f6_cache_load',
 '_h95f10f6_start_auto_search_job','_h95f10f6_search','_h95f10f6_qq_duration_second_chance',
 '_h95f10f6_resolve_qq_duration','_h95f10f6_build_translation_blur','_h95f10f6_translation_blur_fragments',
 '_h95f10f6_draw_blur_translation','_h95f10f6_draw_history_translation','_h95f10f6_install_song_fragment_atlas',
 '_h95f10f6_compact_sync_doctor','_h95f10f6_activate')
for name in required: need(name in funcs,'H95F10F6 function missing: '+name)
_s=src.index(marker)
block=src[_s:src.index('# H95F10F7 bilingual visual-preset parity + long-line containment',_s)]

# Blur parity: final translation blur must share mature H62 progress/material and batch draw.
build_src=ast.get_source_segment(src,funcs['_h95f10f6_build_translation_blur']) or ''
draw_src=ast.get_source_segment(src,funcs['_h95f10f6_draw_blur_translation']) or ''
frag_src=ast.get_source_segment(src,funcs['_h95f10f6_translation_blur_fragments']) or ''
for token in ('_h62_pack_entries_image','_h62_filter_shared_image','H62_BLUR_MID_LEVELS','H62_BLUR_MAX_LEVELS'):
    need(token in build_src,'translation blur material parity missing: '+token)
for token in ('_h62_decay_progress','_h62_decay_mix','drawPixmapFragments','_h95f10f6_translation_blur_fragments'):
    need(token in draw_src,'translation blur final draw parity missing: '+token)
need('shakes=_h95f10f4_translation_shakes(row,text)' in draw_src,'translation shake is not snapshotted once per blur paint')
need('_h95f10f4_translation_shakes' not in frag_src,'blur stage pass advances translation shake more than once')
for bad in ('(-blur,0,.135)','(blur,0,.135)','(0,-blur,.135)','(0,blur,.135)','QPainterPath'):
    need(bad not in draw_src and bad not in frag_src,'final H95F10F6 blur regressed to five-tap/vector hotpath: '+bad)
need("globals()['_h95f7_draw_history_translation']=_h95f10f6_draw_history_translation" in block,'H95F10F6 blur is not final translation-history owner')

# Precise cache quality: ordinary payload in a precise key must be purged, real word clock kept,
# and terminal instrumental payload kept. Execute the helpers without importing the Qt app.
nodes=[]
for name in ('_h95f10f6_precise_cache_row_is_soft','_h95f10f6_purge_soft_precise_cache'):
    node=copy.deepcopy(funcs[name]); node.decorator_list=[]; nodes.append(node)
logs=[]
def quality(text):
    return 3 if str(text).startswith('WORD:') else 1
ns={'_lyric_clock_quality':quality,'write_error_log':lambda *a,**k:logs.append((a,k))}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<h95f10f6-cache>','exec'),ns)
class Lock:
    def __enter__(self): return self
    def __exit__(self,*a): return False
class Panel:
    def __init__(self):
        self._auto_lyric_cache={
            ('QQ音乐','bilingual-pair',True,'track','artist',193):{'lyric':'LINE:lrc','provider_meta':{}},
            ('QQ音乐','bilingual-pair',True,'track2','artist',193):{'lyric':'WORD:qrc','provider_meta':{}},
            ('QQ音乐','bilingual-pair',True,'track3','artist',193):{'lyric':'LINE:pure','provider_meta':{'lyric_payload_instrumental':True}},
            ('QQ音乐','bilingual-pair',False,'track','artist',0):{'lyric':'LINE:fast','provider_meta':{}},
        }
        self._auto_lyric_cache_lock=Lock(); self.persisted=0
    def _persist_auto_lyric_cache(self): self.persisted+=1
panel=Panel(); removed=ns['_h95f10f6_purge_soft_precise_cache'](panel,'')
need(removed==1,'soft precise cache purge did not remove exactly the poisoned ordinary precise row')
need(('QQ音乐','bilingual-pair',True,'track','artist',193) not in panel._auto_lyric_cache,'poisoned precise cache survived')
need(('QQ音乐','bilingual-pair',True,'track2','artist',193) in panel._auto_lyric_cache,'real word-clock precise cache was removed')
need(('QQ音乐','bilingual-pair',True,'track3','artist',193) in panel._auto_lyric_cache,'instrumental terminal cache was removed')
need(('QQ音乐','bilingual-pair',False,'track','artist',0) in panel._auto_lyric_cache,'fast ordinary cache was removed')
need(panel.persisted==1,'precise cache purge did not persist once')

search_src=ast.get_source_segment(src,funcs['_h95f10f6_search']) or ''
for token in ("startswith('LimbusLyric-AutoLyrics-g')",'prefer_precise','_lyric_clock_quality(lyric) < 3','return None, 0'):
    need(token in search_src,'progressive precise soft-result rejection missing: '+token)
need('lyric_payload_instrumental' in search_src,'instrumental exception missing from precise soft-result rejection')

# QQ duration second chance: same 239s candidate->validated is strengthening evidence, not a new
# duration epoch. A pre-bind replay must still be rejected.
node=copy.deepcopy(funcs['_h95f10f6_qq_duration_second_chance']); node.decorator_list=[]
class FakeTime:
    def __init__(self): self.t=100.0
    def monotonic(self): return self.t
    def sleep(self,sec): self.t += float(sec)
class Reader:
    def __init__(self,rows): self.rows=list(rows); self.i=0
    def poll(self,_proc):
        row=self.rows[min(self.i,len(self.rows)-1)]; self.i+=1; return dict(row)
class Media:
    def __init__(self,rows): self._uia_reader=Reader(rows)
    def snapshot(self): return {}
    def _source_matches_process_hint(self,*a): return True
class P:
    def __init__(self,rows): self.media_sync=Media(rows)
    def _same_track(self,*a): return True
fake=FakeTime(); dns={'time':fake,'H95F10F6_QQ_DURATION_SECOND_CHANCE_MS':220.0,'H95F10F6_QQ_DURATION_SECOND_CHANCE_POLL_MS':55.0,
    '_qq_duration_replays_prebind':lambda cand,pre_uia,pre_transport,pre_source: bool(pre_uia and cand==pre_uia),
    'write_error_log':lambda *a,**k:None}
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<h95f10f6-duration>','exec'),dns)
job={'source':'QQ音乐','song':'熱異常','artist':'いよわ','qq_prebind_duration_ms':193000,'qq_prebind_transport_duration_ms':0,'qq_prebind_duration_source':'qq-time-pair-validated'}
rows=[{'duration_ms':239000,'source':'qq-time-pair-candidate'},{'duration_ms':239000,'source':'qq-time-pair-validated'}]
need(dns['_h95f10f6_qq_duration_second_chance'](P(rows),job)==239000,'candidate->validated same duration did not close QQ version witness')
fake.t=200.0; rows2=[{'duration_ms':193000,'source':'qq-time-pair-candidate'},{'duration_ms':193000,'source':'qq-time-pair-validated'}]
need(dns['_h95f10f6_qq_duration_second_chance'](P(rows2),job)==0,'pre-bind old duration replay was admitted by second chance')

# Sync UI: preserve expert controls but hide them by default behind one disclosure.
sync_src=ast.get_source_segment(src,funcs['_h95f10f6_compact_sync_doctor']) or ''
for token in ("'歌词同步医生'","QPushButton('高级同步校准  ▸'",'setCheckable(True)','box.hide()','toggle.toggled.connect'):
    need(token in sync_src,'collapsed Sync Doctor invariant missing: '+token)
need('当前播放器同步微调' in sync_src,'sync disclosure tooltip no longer directs ordinary users to current-player offset')

# Ownership boundary: no timing/parser/seek rewrite in this patch.
for bad in ('MediaSessionSync.position =','MediaSessionSync.seek =','MediaSessionSync.bind_track =','parse_lrc =','LyricWindow.paintEvent='):
    need(bad not in block,'H95F10F6 crossed protected timing/parser/paint authority: '+bad)
print('BILINGUAL BLUR + PRECISE CACHE + SYNC UI H95F10F6 REPLAY: PASS')
print('  bilingual blur uses H62 optical progress + async batched material: PASS')
print('  poisoned ordinary precise cache is purged; word/instrumental entries survive: PASS')
print('  QQ 239s candidate->validated duration witness closes without old-epoch replay: PASS')
print('  advanced Sync Doctor preserved but collapsed by default: PASS')
