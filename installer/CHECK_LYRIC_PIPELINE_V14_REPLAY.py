#!/usr/bin/env python3
import ast, html, re, sys, textwrap
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V14_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src)

def fail(msg):
    print('LYRIC PIPELINE V14 REPLAY: FAIL')
    print('  -', msg)
    raise SystemExit(1)

def class_func(cls,name):
    for node in tree.body:
        if isinstance(node,ast.ClassDef) and node.name==cls:
            for item in node.body:
                if isinstance(item,ast.FunctionDef) and item.name==name:
                    return ast.get_source_segment(src,item)
    fail(f'missing {cls}.{name}')

# Pure payload-provenance helpers, without importing Qt/application runtime.
want_assign={'_LRC_TIME_TOKEN_RE','_LRC_INLINE_TIME_RE','_LRC_OFFSET_RE','_LRC_METADATA_ONLY_RE','_LRC_CREDIT_BODY_RE','_LRC_EXTRA_CREDIT_RE','_LRC_CONTROL_RE','_INSTRUMENTAL_BOILERPLATE_RE'}
want_funcs={'_lrc_fraction_ms','_lrc_match_to_ms','_split_lrc_leading_timestamps','_sanitize_lrc_body','_instrumental_boilerplate_bodies','_instrumental_notice_compact','_instrumental_notice_text_variants','_instrumental_notice_strip_provider_meta','_is_instrumental_boilerplate_payload','_is_netease_sparse_instrumental_placeholder','_provider_pure_music_flag','_lyric_payload_profile','_provider_payload_instrumental','_build_lyric_payload_meta'}
selected=[]
for node in tree.body:
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        targets=node.targets if isinstance(node,ast.Assign) else [node.target]
        names={t.id for t in targets if isinstance(t,ast.Name)}
        if names & want_assign: selected.append(node)
    elif isinstance(node,ast.FunctionDef) and node.name in want_funcs:
        selected.append(node)
ns={'re':re,'html':html}
exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),ns,ns)
payload_inst=ns['_provider_payload_instrumental']; build_meta=ns['_build_lyric_payload_meta']

# The sparse NetEase rule must follow the lyric payload source, not the playback app.
sparse='[00:05.00]静听此刻旋律'
if not payload_inst('网易云', sparse, 116165, {}):
    fail('NetEase sparse payload was not recognized')
if payload_inst('QQ音乐', sparse, 116165, {}):
    fail('source-specific sparse rule leaked into native QQ payloads')
meta=build_meta({'source':'QQ音乐'},'网易云',sparse,116165,{})
if meta.get('source')!='QQ音乐' or meta.get('lyric_payload_source')!='网易云' or not meta.get('lyric_payload_instrumental'):
    fail(f'payload provenance did not preserve QQ transport + NetEase lyric source: {meta}')

# Execute the real high-level search() with provider fakes. This models the V13 感官过载 shape:
# QQ native lyric unavailable -> strict NetEase duration match -> one-row 5s payload -> no KuGou wait.
search_src=class_func('LyricSearchEngine','search')
logs=[]; calls=[]
def log(label,*a,detail=None,**k): logs.append((label,detail))
def quality(text):
    t=str(text or '')
    return 3 if re.search(r'<\d{1,3}:\d{1,2}',t) else (1 if re.search(r'\[\d{1,3}:\d{1,2}',t) else 0)
run_ns=dict(ns)
run_ns.update({
    '_lyric_clock_quality':quality,
    '_verify_precise_enhancement_against_native':lambda ref,cand,**kw:(cand,{'matches':1,'coverage':1.0},'fixture'),
    '_translation_to_line_lrc':lambda a,b:a or '',
    '_extract_native_chinese_lrc':lambda x:'',
    '_merge_translation_native_chinese':lambda a,b:a,
    'write_error_log':log,
})
exec('class E:\n'+textwrap.indent(search_src,'    '),run_ns); E=run_ns['E']; run_ns['LyricSearchEngine']=E
E._provider_meta={}
E._set_provider_meta=classmethod(lambda cls,**m:setattr(cls,'_provider_meta',dict(m)))
E.last_provider_meta=classmethod(lambda cls:dict(getattr(cls,'_provider_meta',{})))
E._is_cancelled=classmethod(lambda cls:False)
E._clean_lrc=classmethod(lambda cls,x,*a:str(x or ''))
E._merge_intro_credits=classmethod(lambda cls,a,b:a)
E._fail=classmethod(lambda cls,provider,exc=None,detail=None:(None,None,0))
def qq(cls,*a,**k):
    calls.append('QQ音乐'); return None,None,116000
def ncm(cls,*a,**k):
    calls.append('网易云'); cls._set_provider_meta(source='网易云',duration_ms=116165); return sparse,None,116165
def kg(cls,*a,**k):
    calls.append('酷狗'); return '[00:01.00]SHOULD_NOT_BE_CALLED',None,116000
E.search_qq=classmethod(qq); E.search_netease=classmethod(ncm); E.search_kugou=classmethod(kg)
E._search_qq_ordinary=classmethod(qq); E._search_netease_ordinary=classmethod(ncm); E._search_kugou_ordinary=classmethod(kg)
out,dur=E.search('感官过载','残像音阶/M3mo','QQ音乐',False,provider_duration_ms=116000,prefer_precise=True)
final_meta=E.last_provider_meta()
if out!=sparse or calls!=['QQ音乐','网易云']:
    fail(f'cross-provider instrumental closure failed: calls={calls} out={out!r}')
if final_meta.get('source')!='QQ音乐' or final_meta.get('lyric_payload_source')!='网易云' or not final_meta.get('lyric_payload_instrumental'):
    fail(f'final search metadata lost transport/payload split: {final_meta}')
if not any(label=='跨平台纯音乐证据提前收口' for label,_ in logs):
    fail('cross-provider instrumental early closure was not diagnosed')

# Provider-switch race recovery must requery lyrics only; no MediaSync rebind/clock reset.
retry_src=class_func('ControlPanel','_requeue_auto_search_for_current_source')
if 'media_sync' in retry_src or '_start_auto_search_job' not in retry_src or 'media-rebind=0' not in retry_src:
    fail('source-switch retry is not isolated to lyric retrieval')
class Toggle:
    def __init__(self,v): self.v=v
    def isChecked(self): return self.v
class Combo:
    def __init__(self,v): self.v=v
    def currentText(self): return self.v
retry_ns={'write_error_log':log}
exec('class P:\n'+textwrap.indent(retry_src,'    '),retry_ns); P=retry_ns['P']; p=P()
p._is_started=True; p._auto_armed=True; p.auto_track_check=Toggle(True); p.source_combo=Combo('QQ音乐'); p.trans_check=Toggle(False); p.precise_tracking_check=Toggle(True); p._auto_generation=10; p._auto_target_key='好结局|银河小鱼'; p._track_identity=lambda s,a:f'{s}|{a}'; captured=[]; p._start_auto_search_job=lambda job:captured.append(dict(job))
if not p._requeue_auto_search_for_current_source({'song':'好结局','artist':'银河小鱼','key':'好结局|银河小鱼','source':'网易云'},'fixture'):
    fail('provider-switch race retry refused a valid current transaction')
if not captured or captured[0].get('source')!='QQ音乐' or captured[0].get('generation')!=11:
    fail(f'provider-switch retry did not target the current source: {captured}')

launch_src=class_func('ControlPanel','_launch_current_lyrics')
for needle in ('阻止新曲搜索期间重启旧歌词', "payload_source == '网易云'", '_active_lyric_provider_meta'):
    if needle not in launch_src: fail(f'launch-path system guard missing: {needle}')
worker_src=class_func('ControlPanel','_start_auto_search_job')
if '纯音乐最低等级快速收口' not in worker_src or 'duration_relaxed_for_instrumental' not in worker_src:
    fail('V15 instrumental lowest-tier latency guard missing')
clear_src=class_func('MediaSessionSync','_kugou_clear_inactive_mouse_events')
if 'log_coalesced=1' not in clear_src:
    fail('inactive KuGou event diagnostics are not coalesced')

print('LYRIC PIPELINE V14/V15 COMPAT REPLAY: PASS')
print('  QQ transport + NetEase borrowed payload provenance: PASS')
print('  borrowed sparse instrumental closes before KuGou fallback: PASS')
print('  provider-switch stale result requeues lyrics without MediaSync rebind: PASS')
print('  old-loaded display, V15 instrumental fast-tier and inactive-log guards present: PASS')
