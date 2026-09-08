#!/usr/bin/env python3
import ast, sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V21_FAST_BACKGROUND_IDENTITY_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)

def fail(msg):
    print('LYRIC PIPELINE V21 FAST BACKGROUND IDENTITY + PROVISIONAL CLOCK REPLAY: FAIL')
    print('  -', msg)
    raise SystemExit(1)

def fn(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name==name:
                    return ast.get_source_segment(src,m)
    fail(f'missing {cls}.{name}')

if not any(f'INSTRUMENTAL-RUNTIME-V{n}' in src for n in range(21, 100)):
    fail('V21+ build marker missing')
poll=fn('MediaSessionSync','_poll_loop')
for needle in ("proc_hint_pre in ('qqmusic', 'kgmusic')", 'media_identity_poll_sec = 0.19', 'try_get_media_properties_async'):
    if needle not in poll:
        fail(f'fast MediaProperties cadence missing: {needle}')
if "else 1.0" not in poll:
    fail('NetEase/other historical media metadata cadence not retained')

consume=fn('ControlPanel','_consume_background_identity_fast')
for needle in ('media_metadata_mono', 'age_ms <= 850.0', 'kugou-gsmtc-fast-event', 'qq-gsmtc-fast-event',
               '_promote_kugou_background_identity_hint', '_promote_qq_background_identity_hint'):
    if needle not in consume:
        fail(f'fast identity consumer missing: {needle}')
for forbidden in ('seek_to(', '_qq_queue_seek(', 'media_sync.bind_track(', 'LyricSearchEngine.search(', '_start_auto_search_job('):
    if forbidden in consume:
        fail(f'fast identity timer polluted playback/network authority: {forbidden}')


for promoter_name in ('_promote_kugou_background_identity_hint','_promote_qq_background_identity_hint'):
    promoter=fn('ControlPanel',promoter_name)
    for needle in ('_auto_failed_track_key', '_auto_failed_until', "split('|', 1)", '_same_track'):
        if needle not in promoter:
            fail(f'failed-track cooldown missing from {promoter_name}: {needle}')

init=fn('ControlPanel','__init__')
for needle in ('_background_identity_timer', 'setInterval(120)', '_consume_background_identity_fast'):
    if needle not in init:
        fail(f'120ms background identity consumer timer missing: {needle}')

release=fn('ControlPanel','_release_deferred_startup_tasks')
if '_background_identity_timer.start()' not in release:
    fail('deferred startup does not start background identity timer')

request=fn('ControlPanel','_request_auto_track')
for needle in ('candidate_since', 'initial_position_ms', 'auto_provisional=True', 'initial_position_ms=initial_position_ms'):
    if needle not in request:
        fail(f'identity timestamp no longer seeds provisional clock: {needle}')

# Critical property: fast identity only shortens observation latency. Existing V20 final
# pending-transaction guard remains before bind/reset, so rapid skips do not create churn.
if request.index('_active_auto_target_matches') > request.index('self.media_sync.bind_track'):
    fail('pending-target guard moved after MediaSync reset')

print('LYRIC PIPELINE V21 FAST BACKGROUND IDENTITY + PROVISIONAL CLOCK REPLAY: PASS')
print('  QQ/KuGou MediaProperties sampling follows ~200ms worker cadence: PASS')
print('  fresh metadata consumed on a dedicated 120ms identity-only timer: PASS')
print('  provisional clock remains seeded from first observed identity evidence: PASS')
print('  seek/clock authority and provider IO remain outside the fast consumer: PASS')
