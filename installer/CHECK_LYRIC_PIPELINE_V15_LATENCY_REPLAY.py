#!/usr/bin/env python3
import ast, re, sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V15_LATENCY_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src)

def fail(msg):
    print('LYRIC PIPELINE V15 LATENCY REPLAY: FAIL')
    print('  -', msg)
    raise SystemExit(1)

def class_func(cls,name):
    for node in tree.body:
        if isinstance(node,ast.ClassDef) and node.name==cls:
            for item in node.body:
                if isinstance(item,ast.FunctionDef) and item.name==name:
                    return ast.get_source_segment(src,item)
    fail(f'missing {cls}.{name}')

worker=class_func('ControlPanel','_start_auto_search_job')
# Structural latency contract: duration proof starts before ordinary search, ordinary uses no
# precise provider APIs, pure music terminates at the fast tier, and precision remains a later pass.
needles=(
    'duration_executor.submit',
    'prefer_precise=False',
    "provider_duration_ms=0",
    '纯音乐最低等级快速收口',
    'word_timing=skip',
    'precise_upgrade=skip',
    '自动歌词快速首屏',
    '自动歌词精确升级完成',
)
for n in needles:
    if n not in worker: fail(f'missing progressive latency contract: {n}')
if worker.index('duration_executor.submit') > worker.index('prefer_precise=False'):
    fail('QQ duration proof is still started after ordinary lyric retrieval')
if '_resolve_qq_auto_track_duration_after_bind(job' in worker.split('if progressive:',1)[0]:
    fail('QQ duration proof is still serialized before the progressive stage')

# Pure card result must not inherit an unverified provider candidate duration as playback time.
if "pure_duration = int(identity_duration_ms or job.get('provider_duration_ms') or 0)" not in worker:
    fail('instrumental fast tier still binds provider candidate duration to playback')
if "lyric_candidate_duration_ms" not in worker or 'duration_relaxed_for_instrumental' not in worker:
    fail('instrumental relaxed-duration provenance is missing')

# Precision upgrade must be a lyric hot-swap, never a second MediaSync bind.
on_result=class_func('ControlPanel','_on_auto_lyric_result')
for n in ('same_loaded_for_upgrade','自动歌词精确升级热替换','自动歌词快速首屏沿用预绑定','media-rebind=0'):
    if n not in on_result: fail(f'precision hot-swap guard missing: {n}')
seg=on_result[on_result.index('if same_loaded_for_upgrade:'):on_result.index('else:',on_result.index('if same_loaded_for_upgrade:'))]
if 'bind_track' in seg:
    fail('precision upgrade branch still rebinds MediaSync')
if '自动歌词精确升级失败保留快速歌词' not in worker or '自动歌词精确升级异常保留快速歌词' not in worker:
    fail('precision failure can still downgrade a successful fast-display transaction')

# A manual click while auto-fetch is active must coalesce rather than cancel/start duplicate IO.
manual=class_func('ControlPanel','fetch_lyric')
for n in ('手动抓词已合并当前自动任务','duplicate-network=skip','_auto_fetch_in_progress'):
    if n not in manual: fail(f'manual/auto coalescing missing: {n}')
coalesce_pos=manual.index('手动抓词已合并当前自动任务')
cancel_pos=manual.index('_cancel_auto_jobs')
if coalesce_pos > cancel_pos:
    fail('manual request is still cancelling auto jobs before coalescing')

# Low-level provider/clock methods are not part of the latency patch.
for locked in ('search_qq','search_kugou','search_netease'):
    body=class_func('LyricSearchEngine',locked)
    if 'INSTRUMENTAL-RUNTIME-V15' in body:
        fail(f'provider core {locked} was unnecessarily version-patched')

print('LYRIC PIPELINE V15 LATENCY REPLAY: PASS')
print('  QQ duration proof overlaps ordinary retrieval instead of serializing: PASS')
print('  pure music terminates at ordinary tier with relaxed duration and no word probe: PASS')
print('  normal songs can fast-display then precision hot-swap without MediaSync rebind: PASS')
print('  manual click coalesces with active auto fetch instead of duplicating provider IO: PASS')
