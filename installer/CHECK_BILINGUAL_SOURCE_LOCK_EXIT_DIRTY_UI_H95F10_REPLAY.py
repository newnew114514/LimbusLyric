#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, re, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_BILINGUAL_SOURCE_LOCK_EXIT_DIRTY_UI_H95F10_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ BILINGUAL SOURCE LOCK + EXIT DIRTY CLOSURE + UI STABILITY H95F10' in src,'H95F10 build tag missing')
need('# H95F10 bilingual source lock + exit dirty closure + shell stability' in src,'H95F10 runtime marker missing')
# Search contract: bilingual main+translation is selected as one provider pair, while the
# translation-only sidecar is explicitly forbidden from cross-provider borrowing.
search=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='LyricSearchEngine')
search_fn=next(n for n in search.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=='search')
args=[a.arg for a in search_fn.args.args]
need('provider_locked' in args and 'require_translation_pair' in args,'source-lock search parameters missing')
search_src=ast.get_source_segment(src,search_fn) or ''
for token in (
    "if bool(require_translation_pair) and not trans_only and not provider_locked:",
    "pair_order = [source] + [p for p in ('网易云', 'QQ音乐', '酷狗') if p != source]",
    "if not main_payload.strip() or not line_trans.strip():",
    "if not trans_only and not bilingual_pair_locked:",
    "borrow_order = () if provider_locked else",
    "provider-mix=0",
): need(token in search_src,'same-provider bilingual selection missing: '+token)
# Sidecar follows actual payload provenance, not merely selected/player source.
for token in (
    "payload_meta.get('lyric_payload_source')",
    "prefer_precise=False,provider_locked=True",
    "H95F10双语翻译缓存来源拒绝",
    "current_source!=cached_source",
    "native_pair_coverage < 0.90",
    "_remember_bilingual_pair",
    "_cached_bilingual_pair_translation",
    "H95F10双语翻译复用同源配对",
    "network-refetch=0",
): need(token in src,'translation pair/source lock missing: '+token)
# Auto search cache must separate bilingual-pair payloads while preserving the historical
# ordinary tuple shape used by persisted caches and H83 NetEase identity recovery.
need("mode_slot = 'bilingual-pair' if bool(bilingual_pair) else trans_only" in src,'bilingual auto-cache namespace not isolated')
need(src.count('cache_key_for(requested_precise, identity_duration_ms, bilingual_pair)')>=2,'final/precise cache keys do not carry bilingual namespace')
need('cache_key_for(False, 0, bilingual_pair)' in src and 'cache_key_for(True, pure_duration, bilingual_pair)' in src,'fast/instrumental cache keys do not carry bilingual namespace')
need("source, mode_slot, bool(precise_flag), str(job.get('key') or '')" in src,'bilingual cache key shifted historical track identity index')
need('require_translation_pair=False,' in src,'R2.1 fast auto search no longer preserves first-screen bilingual nonblocking policy')
need(src.count('require_translation_pair=bool(bilingual_pair)')>=1,'precise auto search no longer requires the bilingual pair')

# The actual runtime search authority is wrapped by H14 and then H95F8. Both wrappers must
# accept and forward the new source-lock policy or real auto/manual calls will TypeError even
# though the base LyricSearchEngine.search function passes an isolated AST replay.
top_funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for wrapper_name in ('_limbus_h14_auto_precise_search','_h95f8_search'):
    node=top_funcs.get(wrapper_name); need(node is not None,'runtime search wrapper missing: '+wrapper_name)
    wrapper_args=[a.arg for a in node.args.args]
    need('provider_locked' in wrapper_args and 'require_translation_pair' in wrapper_args,'runtime wrapper policy args missing: '+wrapper_name)
    wrapper_src=ast.get_source_segment(src,node) or ''
    if wrapper_name=='_limbus_h14_auto_precise_search':
        need("kwargs['provider_locked'] = True" in wrapper_src and "kwargs['require_translation_pair'] = True" in wrapper_src and 'call_previous_search()' in wrapper_src,'runtime wrapper policy forwarding missing: '+wrapper_name)
    else:
        need('provider_locked=provider_locked' in wrapper_src and 'require_translation_pair=require_translation_pair' in wrapper_src,'runtime wrapper policy forwarding missing: '+wrapper_name)

# Execute the real search() AST against deterministic provider fixtures. This proves the
# behavioral rule rather than only checking strings: if QQ has main lyric but no translation
# and NetEase has both for the same duration, both displayed halves come from NetEase.
import copy, hashlib, threading, time
from collections import OrderedDict
search_exec=copy.deepcopy(search_fn); search_exec.decorator_list=[]
exec_ns={}
exec(compile(ast.fix_missing_locations(ast.Module(body=[search_exec],type_ignores=[])),'<h95f10-search>','exec'),exec_ns)
real_search=exec_ns['search']
provider_calls=[]
class FakeSearch:
    last_error=''; meta={}; remembered=[]
    @classmethod
    def _set_provider_meta(cls,**meta): cls.meta=dict(meta or {})
    @classmethod
    def last_provider_meta(cls): return dict(cls.meta)
    @classmethod
    def _is_cancelled(cls): return False
    @classmethod
    def _clean_lrc(cls,v,*a,**k): return str(v or '').strip()
    @classmethod
    def _merge_intro_credits(cls,a,b): return a
    @classmethod
    def _remember_bilingual_pair(cls,song,artist,source,duration,main,trans):
        cls.remembered.append((source,int(duration or 0),main,trans)); return True
    @classmethod
    def search_qq(cls,*a,**k):
        provider_calls.append('QQ音乐'); cls._set_provider_meta(source='QQ音乐',lyric_payload_source='QQ音乐'); return FIX['QQ音乐']
    _search_qq_ordinary=search_qq
    @classmethod
    def search_netease(cls,*a,**k):
        provider_calls.append('网易云'); cls._set_provider_meta(source='网易云',lyric_payload_source='网易云'); return FIX['网易云']
    _search_netease_ordinary=search_netease
    @classmethod
    def search_kugou(cls,*a,**k):
        provider_calls.append('酷狗'); cls._set_provider_meta(source='酷狗',lyric_payload_source='酷狗'); return FIX['酷狗']
    _search_kugou_ordinary=search_kugou
FakeSearch.search=staticmethod(real_search)
def lrc(prefix,n=4): return '\n'.join(f'[00:{i:02d}.00]{prefix}{i}' for i in range(n))
def parsed(v,diagnostics=False):
    return [(i*1000,line.split(']',1)[-1],None) for i,line in enumerate(str(v or '').splitlines()) if ']' in line]
def build_meta(primary,payload_source,payload_text,duration,payload_meta):
    out=dict(primary or {}); out.update(dict(payload_meta or {})); out['lyric_payload_source']=str(payload_source or ''); out['duration_ms']=int(duration or 0); return out
run_ns=real_search.__globals__
run_ns.update({
    'LyricSearchEngine':FakeSearch,'_translation_to_line_lrc':lambda t,m:str(t or ''),
    'parse_lrc':parsed,'_lyric_clock_quality':lambda v:1,'_provider_payload_instrumental':lambda *a,**k:False,
    '_build_lyric_payload_meta':build_meta,'_extract_native_chinese_lrc':lambda v:'',
    '_merge_translation_native_chinese':lambda a,b:a,'write_error_log':lambda *a,**k:None,
    'hashlib':hashlib,'threading':threading,'time':time,'OrderedDict':OrderedDict,'re':re,
})
# Preferred QQ is missing translation; NetEase pair must replace both halves.
FIX={'QQ音乐':(lrc('Q'),None,200000),'网易云':(lrc('N'),lrc('T'),200200),'酷狗':(lrc('K'),None,200100)}
provider_calls.clear(); FakeSearch.remembered.clear(); FakeSearch.meta={}
out,dur=FakeSearch.search('song','artist','QQ音乐',False,provider_duration_ms=200000,prefer_precise=True,require_translation_pair=True)
need(out==lrc('N'),'functional pair selection kept QQ main while borrowing translation')
need(FakeSearch.meta.get('lyric_payload_source')=='网易云','functional pair provenance is not the provider owning both halves')
need(FakeSearch.remembered and FakeSearch.remembered[-1][0]=='网易云' and FakeSearch.remembered[-1][3]==lrc('T'),'validated translation was not handed off as the exact same-provider pair')
# Preferred provider already has a complete pair: do not serially query all three providers.
FIX={'QQ音乐':(lrc('Q',10),lrc('QT',10),200000),'网易云':(lrc('N',10),lrc('NT',10),200000),'酷狗':(lrc('K',10),lrc('KT',10),200000)}
provider_calls.clear(); FakeSearch.remembered.clear(); FakeSearch.meta={}
out,_=FakeSearch.search('song','artist','QQ音乐',False,provider_duration_ms=200000,prefer_precise=True,require_translation_pair=True)
need(out==lrc('Q',10) and provider_calls==['QQ音乐'],'complete native pair still causes unnecessary foreign-provider probes')
# Provider-locked translation-only fallback must not call another source.
FIX={'QQ音乐':(lrc('Q'),None,200000),'网易云':(lrc('N'),lrc('NT'),200000),'酷狗':(lrc('K'),lrc('KT'),200000)}
provider_calls.clear(); FakeSearch.meta={}
out,_=FakeSearch.search('song','artist','QQ音乐',True,provider_duration_ms=200000,prefer_precise=False,provider_locked=True)
need(out is None and provider_calls==['QQ音乐'],'provider_locked translation-only search still borrowed another provider')

# Terminal dirty cleanup must union the translation lane into the exact H72 helper used by
# final retirement; otherwise stale translation pixels survive after the main row disappears.
for token in (
    "_H95F10_H72_REGION_PRE = globals().get('_h72_held_visual_region')",
    "item._h72_last_dirty_region = base.united(region)",
    "globals()['_h72_held_visual_region'] = _h95f10_translation_retire_region",
    "_h95f10_translation_last_dirty_region",
): need(token in src,'terminal bilingual dirty closure missing: '+token)
# Pre-first-row badge is semantic/stable and width-bounded; it must not alter timing authority.
for token in (
    "text = '等待歌词'",
    "text = '读取中'",
    "badge.setMinimumWidth(int(H95F10_SYNC_BADGE_WIDTH))",
    "player clock authority unchanged",
): need(token in src,'sync badge stabilization missing: '+token)
# Explicit frontend naming + requested translucent top glass.
need("combo.addItem('新版','studio')" in src and "combo.addItem('旧版','legacy')" in src,'新版/旧版 names missing')
for name,expected in [('H95F7_MODERN_CLASSIC_ALPHA',122),('H95F7_MODERN_STUDIO_ALPHA',116)]:
    m=re.search(rf'{name}\s*=\s*(\d+)',src); need(m and int(m.group(1))==expected,f'{name} is not the reviewed 40-50% alpha')
# H95F10 is presentation/data-source policy only; no clock/seek monkeypatches are allowed.
block=src[src.index('# H95F10 bilingual source lock + exit dirty closure + shell stability'):src.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync.position =','MediaSessionSync.seek =','LyricWindow._playback_position =','parse_lrc ='):
    need(bad not in block,'H95F10 crossed protected timing/parser authority: '+bad)
print('BILINGUAL SOURCE LOCK + EXIT DIRTY + UI H95F10 REPLAY: PASS')
print('  functional same-provider fallback + exact pair handoff + cache isolation: PASS')
print('  translation terminal dirty-region closure: PASS')
print('  pre-first-row sync badge stability: PASS')
print('  exact 新版/旧版 naming + 40-50% top glass: PASS')
