#!/usr/bin/env python3
import ast
from pathlib import Path
import re
import sys
import textwrap

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_PRECISION_LADDER_QQ_BACKGROUND_REPLAY.py <main.py>')
path = Path(sys.argv[1]); src = path.read_text(encoding='utf-8'); tree = ast.parse(src)

def fail(msg):
    print('PRECISION LADDER + QQ BACKGROUND REPLAY: FAIL')
    print('  -', msg)
    raise SystemExit(1)

def func_source(cls, name):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name:
                    return ast.get_source_segment(src, item)
    fail(f'missing {cls}.{name}')

def const(name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    fail(f'missing constant {name}')

# ---------- retrieval policy / quality ladder ----------
search_src = func_source('LyricSearchEngine', 'search')
netease_src = func_source('LyricSearchEngine', 'search_netease')
qq_src = func_source('LyricSearchEngine', 'search_qq')
kugou_src = func_source('LyricSearchEngine', 'search_kugou')
ncm_ord_src = func_source('LyricSearchEngine', '_search_netease_ordinary')
qq_ord_src = func_source('LyricSearchEngine', '_search_qq_ordinary')
kg_ord_src = func_source('LyricSearchEngine', '_search_kugou_ordinary')
for needle in (
    'prefer_precise=True',
    'native precise > verified foreign precise > native ordinary > safe foreign ordinary',
    '跨平台逐字质量阶梯命中',
    'ordinary_only = not bool(prefer_precise)',
):
    if needle not in search_src:
        fail(f'missing quality-ladder wiring: {needle}')
# Protected provider methods keep their historical signatures/source contracts. Classic mode
# is implemented by separate line-LRC-only helpers instead of changing those methods.
if 'prefer_precise' in netease_src.split(':',1)[0] or 'prefer_precise' in qq_src.split(':',1)[0] or 'prefer_precise' in kugou_src.split(':',1)[0]:
    fail('protected provider method signature was changed for classic mode')
if '网易云经典模式普通LRC命中' not in ncm_ord_src or '_fetch_netease_word_lyric' in ncm_ord_src:
    fail('NetEase ordinary-only helper missing or probes word timing')
if 'QQ经典模式普通LRC命中' not in qq_ord_src or 'fcg_search_pc_lrc' in qq_ord_src or 'qrc.fcg' in qq_ord_src or 'fetch_qq_qrc' in qq_ord_src:
    fail('QQ ordinary-only helper missing or contains QRC retrieval')
if '酷狗经典模式普通LRC命中' not in kg_ord_src or "'https://lyrics.kugou.com" in kg_ord_src or '"https://lyrics.kugou.com' in kg_ord_src:
    fail('Kugou ordinary-only helper missing or probes KRC service')
if any('_LRC_INLINE_TIME_RE.sub' not in part for part in (ncm_ord_src, qq_ord_src, kg_ord_src)):
    fail('classic ordinary-only helpers do not defensively strip inline word timing')

# Build a tiny executable LyricSearchEngine with only search(), provider fakes, and helpers.
logs=[]; calls=[]
ORD='[00:00.00]alpha\n[00:10.00]beta\n[00:20.00]gamma\n[00:30.00]delta'
PRE='[00:00.00]<00:00.00>alpha<00:01.00>\n[00:10.00]<00:10.00>beta<00:11.00>\n[00:20.00]<00:20.00>gamma<00:21.00>\n[00:30.00]<00:30.00>delta<00:31.00>'

def quality(text):
    t=str(text or '')
    return 3 if re.search(r'<\d{1,3}:\d{1,2}', t) else (1 if re.search(r'\[\d{1,3}:\d{1,2}', t) else 0)

def verify(ref, cand, **kwargs):
    return cand, {'matches':4,'coverage':1.0}, 'fixture-aligned'

def log(label,*a,detail=None,**k): logs.append((label,detail))

instrumental_gate={'value':False}
ns={
    '_lyric_clock_quality':quality,
    '_provider_payload_instrumental':lambda source,text,duration_ms=0,provider_meta=None: bool(instrumental_gate['value']),
    '_build_lyric_payload_meta':lambda base,source,text,duration_ms=0,provider_meta=None: dict(base or {}, lyric_payload_source=source, lyric_payload_instrumental=bool(instrumental_gate['value'])),
    '_verify_precise_enhancement_against_native':verify,
    '_translation_to_line_lrc':lambda a,b:a or '',
    '_extract_native_chinese_lrc':lambda x:'',
    '_merge_translation_native_chinese':lambda a,b:a,
    'write_error_log':log,
}
method=textwrap.indent(search_src,'    ')
exec('class E:\n'+method,ns); E=ns['E']; ns['LyricSearchEngine']=E
E._provider_meta={}
E._set_provider_meta=classmethod(lambda cls, **meta: setattr(cls,'_provider_meta',dict(meta)))
E.last_provider_meta=classmethod(lambda cls: dict(getattr(cls,'_provider_meta',{})))
E._is_cancelled=classmethod(lambda cls: False)
E._clean_lrc=classmethod(lambda cls, x, *a: str(x or ''))
E._merge_intro_credits=classmethod(lambda cls, a, b: a)
E._fail=classmethod(lambda cls, provider, exc=None, detail=None: (None,None,0))

def configure(primary='ordinary', qq='ordinary', kg='precise'):
    calls.clear(); logs.clear()
    def ncm_precise(cls,*args,**kwargs):
        calls.append(('网易云','precise'))
        cls._set_provider_meta(source='网易云', netease_song_id='2620847344', duration_ms=224571)
        return ({'precise':PRE,'ordinary':ORD,'none':None}[primary], None, 224571)
    def qq_precise(cls,*args,**kwargs):
        calls.append(('QQ音乐','precise'))
        return ({'precise':PRE,'ordinary':ORD,'none':None}[qq], None, 223000)
    def kg_precise(cls,*args,**kwargs):
        calls.append(('酷狗','precise'))
        return ({'precise':PRE,'ordinary':ORD,'none':None}[kg], None, 223000)
    def ncm_ord(cls,*args,**kwargs):
        calls.append(('网易云','ordinary'))
        cls._set_provider_meta(source='网易云', netease_song_id='2620847344', duration_ms=224571)
        return ({'precise':ORD,'ordinary':ORD,'none':None}[primary], None, 224571)
    def qq_ord(cls,*args,**kwargs):
        calls.append(('QQ音乐','ordinary'))
        return ({'precise':ORD,'ordinary':ORD,'none':None}[qq], None, 223000)
    def kg_ord(cls,*args,**kwargs):
        calls.append(('酷狗','ordinary'))
        return ({'precise':ORD,'ordinary':ORD,'none':None}[kg], None, 223000)
    E.search_netease=classmethod(ncm_precise); E.search_qq=classmethod(qq_precise); E.search_kugou=classmethod(kg_precise)
    E._search_netease_ordinary=classmethod(ncm_ord); E._search_qq_ordinary=classmethod(qq_ord); E._search_kugou_ordinary=classmethod(kg_ord)

# Precise: native ordinary must lose to verified foreign precise. Keep native/player duration.
configure(primary='ordinary', qq='ordinary', kg='precise')
out,dur=E.search('烂尾楼','程墨INK','网易云',False,provider_duration_ms=224571,prefer_precise=True)
if quality(out)!=3 or dur!=224571:
    fail(f'precise ladder did not select foreign precise while preserving native duration: q={quality(out)} dur={dur}')
if not any(c == ('酷狗','precise') for c in calls):
    fail('precise ladder never probed Kugou precise candidate')
if not any(x[0]=='跨平台逐字质量阶梯命中' for x in logs):
    fail('precise ladder hit was not diagnosed')

# Instrumental primary: selected provider's own notice must stop the foreign precise ladder.
configure(primary='ordinary', qq='precise', kg='precise')
instrumental_gate['value'] = True
out,dur=E.search('纯音乐测试','Artist','网易云',False,provider_duration_ms=224571,prefer_precise=True)
if calls != [('网易云','precise')]:
    fail(f'instrumental primary still queried foreign providers: {calls}')
if not any(x[0]=='纯音乐主源快速收口' for x in logs):
    fail('instrumental primary fast-path was not diagnosed')
instrumental_gate['value'] = False

# Classic: own ordinary wins immediately and no foreign provider is queried for enhancement.
configure(primary='ordinary', qq='precise', kg='precise')
out,dur=E.search('烂尾楼','程墨INK','网易云',False,provider_duration_ms=224571,prefer_precise=False)
if quality(out)!=1:
    fail('classic mode did not stay ordinary')
if calls != [('网易云','ordinary')]:
    fail(f'classic mode did not stop at native ordinary helper: {calls}')

# Classic with missing native lyric may borrow, but every provider must still be ordinary-only.
configure(primary='none', qq='ordinary', kg='precise')
out,dur=E.search('x','y','网易云',False,provider_duration_ms=224571,prefer_precise=False)
if quality(out)!=1:
    fail('classic missing-native fallback did not choose ordinary lyric')
if any(kind != 'ordinary' for _provider, kind in calls):
    fail(f'classic fallback enabled precise probing: {calls}')

# Auto cache must split precise/classic mode.
if "bool(job.get('prefer_precise', True))" not in src:
    fail('auto lyric cache/search path does not carry precise mode')
if "'prefer_precise': bool(self.precise_tracking_check.isChecked())" not in src:
    fail('auto track job does not capture precise/classic mode')

# ---------- QQ hidden-window display-only bootstrap ----------
helper_src=func_source('MediaSessionSync','_qq_background_display_local_position')
poll_src=func_source('MediaSessionSync','_poll_loop')
if "position_source = 'qq-background-metadata-local'" not in poll_src:
    fail('QQ background display lane not published')
if '_qq_background_display_track_key' not in helper_src:
    fail('QQ background display engagement is not track-scoped')
if 'authority=display-only' not in helper_src:
    fail('QQ background lane is not explicitly display-only')

class FakeTime:
    def __init__(self): self.ms=100000.0
    def monotonic(self): return self.ms/1000.0
T=FakeTime()
ns2={
    'time':T, '_clean_name':lambda x: re.sub(r'[^a-z0-9]+','',str(x or '').lower()),
    'QQ_BACKGROUND_DISPLAY_LOCAL_ENABLED':True,
    'QQ_BACKGROUND_DISPLAY_LOCAL_GRACE_MS':const('QQ_BACKGROUND_DISPLAY_LOCAL_GRACE_MS'),
    'QQ_BACKGROUND_DISPLAY_LOCAL_MAX_INITIAL_MS':const('QQ_BACKGROUND_DISPLAY_LOCAL_MAX_INITIAL_MS'),
    'write_error_log':log,
}
exec('class H:\n'+textwrap.indent(helper_src,'    '),ns2); H=ns2['H']

def make(title='Holding On', source='QQMusic.exe', initial=600.0, status='playing'):
    h=H(); h._auto_local_active=True; h._qq_auto_local_seed_reason='auto-track'; h._uia_duration_ms=205000
    h._auto_local_started_mono=T.ms-2200; h._auto_local_position_ms=float(initial); h._auto_local_anchor_mono=T.ms-2200
    h._auto_local_status='playing'; h._qq_background_display_local_engaged=False; h._qq_background_display_track_key=''
    h._track_key='holdingon|adibsinsalsa'
    h._state={'media_title':title,'media_artist':'Adib Sin/Salsa','media_source':source}
    h._source_matches_process_hint=lambda a,b: str(a).lower().startswith('qqmusic')
    def local(st):
        if h._auto_local_status=='playing': h._auto_local_position_ms += max(0,T.ms-h._auto_local_anchor_mono)
        h._auto_local_anchor_mono=T.ms; h._auto_local_status=st
        return int(h._auto_local_position_ms)
    h._auto_local_position=local
    return h

h=make(); pos=h._qq_background_display_local_position('playing')
if pos is None or pos < 2000 or not h._qq_background_display_local_engaged:
    fail(f'QQ background metadata-confirmed local clock did not engage: {pos}')
h=make(title='Other Song')
if h._qq_background_display_local_position('playing') is not None:
    fail('wrong QQ metadata title engaged background clock')
h=make(source='cloudmusic.exe')
if h._qq_background_display_local_position('playing') is not None:
    fail('wrong media source engaged QQ background clock')
h=make(initial=9000.0)
if h._qq_background_display_local_position('playing') is not None:
    fail('very-late provisional candidate engaged inaccurate QQ background clock')
h=make(status='paused')
if h._qq_background_display_local_position('paused') is not None:
    fail('paused track may not establish a new background-zero estimate')

print('PRECISION LADDER + QQ BACKGROUND REPLAY: PASS')
print('  precise: native precise > verified foreign precise > native ordinary > safe foreign ordinary: PASS')
print('  classic: ordinary-only provider retrieval; no word-timing enhancement probes: PASS')
print('  auto cache separates precise/classic retrieval mode: PASS')
print('  QQ hidden-window auto track may use metadata-confirmed display-only local clock: PASS')
print('  wrong title/source/late candidate/paused bootstrap remain rejected: PASS')
