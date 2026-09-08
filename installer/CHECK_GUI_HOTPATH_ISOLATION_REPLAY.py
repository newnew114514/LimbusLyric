#!/usr/bin/env python3
from __future__ import annotations
import ast, sys
from pathlib import Path

if len(sys.argv) != 2:
    print('usage: CHECK_GUI_HOTPATH_ISOLATION_REPLAY.py <main.py>')
    raise SystemExit(2)
path = Path(sys.argv[1])
source = path.read_text(encoding='utf-8')
tree = ast.parse(source, filename=str(path))

classes = {n.name:n for n in tree.body if isinstance(n, ast.ClassDef)}
def method(cls, name):
    return next((n for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name), None)
def src(node):
    return ast.get_source_segment(source,node) or ''
def calls(node, name):
    out=[]
    for n in ast.walk(node):
        if isinstance(n,ast.Call):
            f=n.func
            if isinstance(f,ast.Attribute) and f.attr==name: out.append(n)
            elif isinstance(f,ast.Name) and f.id==name: out.append(n)
    return out

def need(cond, msg):
    if not cond:
        print('GUI HOTPATH ISOLATION REPLAY: FAIL '+msg)
        raise SystemExit(1)
    print('  '+msg+': PASS')

ms=classes.get('MediaSessionSync'); lw=classes.get('LyricWindow')
need(ms is not None and lw is not None, 'core classes present')

snap=method(ms,'snapshot'); ncm=method(ms,'_netease_poll_page_interaction'); qq=method(ms,'_qq_poll_pointer_gesture')
probe=method(ms,'_request_click_target_probe'); consume=method(ms,'_consume_click_target_probe')
kg=method(ms,'_kugou_consume_hooked_mouse_events')
kg_poll=method(ms,'_kugou_poll_pointer_gesture')
kg_cached=method(ms,'_kugou_hotpath_cached_window_rect')
need(all((snap,ncm,qq,probe,consume,kg,kg_poll,kg_cached)), 'hotpath methods present')

# The expensive process image lookup must be owned only by the daemon verifier worker,
# never by snapshot/provider gesture functions.
need(not calls(snap,'_process_stem_at_point'), 'snapshot has no synchronous process-image lookup')
need(not calls(ncm,'_process_stem_at_point'), 'NetEase click polling has no synchronous process-image lookup')
need(not calls(qq,'_process_stem_at_point'), 'QQ gesture polling has no synchronous process-image lookup')
need(calls(probe,'_process_stem_at_point'), 'async verifier owns process-image lookup')
need('threading.Thread' in src(probe) and 'daemon=True' in src(probe), 'click verifier is daemon-threaded')
need("_request_click_target_probe" in src(ncm) and "_consume_click_target_probe" in src(ncm), 'NetEase click target is request/consume async')
need("_request_click_target_probe" in src(qq) and "_consume_click_target_probe" in src(qq), 'QQ nonrail target is request/consume async')

# KuGou's global hook may be installed, but window discovery must happen only after the
# queue proves there is an event to interpret.
kg_text=src(kg)
idx_events=kg_text.find('if not events:')
idx_rect=kg_text.find('rect_now = self._kugou_window_rect()')
need(idx_events >= 0, 'KuGou hook queue emptiness is checked')
need(not calls(kg,'_kugou_window_rect'), 'KuGou hook consumer has no synchronous window discovery')
need(not calls(kg_poll,'_kugou_window_rect'), 'KuGou polling fallback has no synchronous window discovery')
need('_kugou_physical_rect_cache' in src(kg_cached) and '_kugou_last_main_rect' in src(kg_cached), 'KuGou hotpath geometry is cache-only')
need('_kugou_deferred_mouse_events' in src(kg), 'KuGou hook event is deferred losslessly when geometry is missing')

# Atlas is a visual optimization. It gets one worker at a time, a build-time fuse, and
# prepares QRectF metadata off the GUI thread. Timing/seek code is not involved.
build_fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_build_song_fragment_atlas_image'),None)
schedule=method(lw,'_schedule_song_fragment_atlas'); install=method(lw,'_install_song_fragment_atlas')
need(all((build_fn,schedule,install)), 'atlas methods present')
need('SONG_FRAGMENT_ATLAS_BUILD_BUDGET_MS' in source and 'SONG_FRAGMENT_ATLAS_INSTALL_FUSE_MS' in source, 'atlas adaptive budgets declared')
need('if inflight:' in src(schedule) and "return 'deferred-inflight'" in src(schedule), 'atlas has single-heavy-worker admission')
need('performance_budget_hit' in src(schedule), 'atlas worker has cooperative build budget')
need('QRectF(' in src(build_fn), 'atlas metadata is prepared in worker')
need('_song_fragment_atlas_performance_fused' in src(install) and 'fallback=sprite-fragment' in src(install), 'atlas slow-machine fuse falls back visually only')
need('position_ms' not in src(install) and 'seek_serial' not in src(install), 'atlas fuse cannot edit media clock/seek state')

# The performance patch should be observable in diagnostics without changing renderer cadence.
need('GUI HOTPATH-ISOLATION H8' in source, 'H8 build tag present')
need('RUNTIME-ISOLATION CLOSURE H8F2' in source, 'H8F2 runtime-isolation closure present')
need('RENDER_ANIMATION_TICK_MIN_MS = 12' in source and 'RENDER_ANIMATION_TICK_MAX_MS = 16' in source, 'existing render cadence preserved')
print('GUI HOTPATH ISOLATION REPLAY: PASS')
