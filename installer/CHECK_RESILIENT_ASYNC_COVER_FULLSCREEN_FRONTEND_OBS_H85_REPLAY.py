"""H85 resilient async / instant cover / fullscreen / frontend / OBS replay."""
import ast, asyncio, sys, time
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(sys.argv[1]).resolve(); main=next(root.glob('LimbusLyric_*.py')); src=main.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def fn(name):
    n=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    return ast.get_source_segment(src,n) or '',n
ck('H85 build tag','+ RESILIENT ASYNC + INSTANT COVER + FULLSCREEN + FRONTEND + OBS H85' in src)
old_cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='MediaSessionSync')
old_poll=next(n for n in old_cls.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='_poll_loop')
old=ast.get_source_segment(src,old_poll) or ''
ck('H84 historical poll kept intact','await GlobalSystemMediaTransportControlsSessionManager.request_async()' in old and 'await session.try_get_media_properties_async()' in old)
h85,_=fn('_h85_poll_loop')
ck('H85 manager no blocking await','await GlobalSystemMediaTransportControlsSessionManager.request_async()' not in h85 and "manager_request = {}" in h85)
ck('H85 metadata no blocking await','await session.try_get_media_properties_async()' not in h85 and "metadata_request = {}" in h85)
ck('H85 uses manager single slot',"kind='manager'" in h85 and '_h85_media_request_slot' in h85)
ck('H85 uses metadata single slot',"kind='metadata'" in h85 and 'media_identity_poll_sec' in h85)
ck('H84 owner checks retained',h85.count("poll_owner != (")>=3)
ck('final publication owner retained','self._set_state(_poll_owner=poll_owner, **update)' in h85)
helper,hnode=fn('_h85_media_request_slot')
ck('cancelled task retains slot until done',"return False, None" in helper and "slot['task'] = None" in helper and 'task.done()' in helper)
ck('owner change cancels old request',"owner_changed = owner != slot.get('owner')" in helper and 'task.cancel()' in helper)
ck('timeout does not stop position loop','position-poll=continues' in helper)
# Execute helper in a real asyncio loop.
ns={'asyncio':asyncio,'time':time,'write_error_log':lambda *a,**k:None}; exec(compile(ast.Module(body=[hnode],type_ignores=[]),str(main),'exec'),ns); helper_fn=ns['_h85_media_request_slot']
async def request_once(): await asyncio.sleep(.01); return 'ok'
async def async_replay():
    slot={}; ready,val=helper_fn(slot,'A',request_once,timeout=.3,interval=0.0); started=slot.get('task') is not None and not ready
    await asyncio.sleep(.02); ready,val=helper_fn(slot,'A',request_once,timeout=.3,interval=.2); delivered=ready and val=='ok'
    # owner switch cancels one old slot and does not create a second while cancellation is pending
    gate=asyncio.Event()
    async def slow(): await gate.wait(); return 'late'
    s={}; helper_fn(s,'OLD',slow,timeout=5,interval=0); oldtask=s.get('task'); helper_fn(s,'NEW',request_once,timeout=5,interval=0)
    bounded=(s.get('task') is oldtask and bool(s.get('cancelled')))
    try: await oldtask
    except BaseException: pass
    helper_fn(s,'NEW',request_once,timeout=5,interval=0); recovered=s.get('task') is not None and s.get('owner')=='NEW'
    if s.get('task'): s['task'].cancel()
    return started,delivered,bounded,recovered
r=asyncio.run(async_replay()); ck('async request starts without blocking',r[0]); ck('completed request publishes on later poll',r[1]); ck('owner switch remains single-slot bounded',r[2]); ck('new owner recovers after old slot retires',r[3])
cover,_=fn('_h85_record_loaded_track'); load,_=fn('_h85_load_cover_cache'); write,_=fn('_h85_write_cover_cache')
ck('cover cache is persistent and bounded','cover_color_cache_v1.json' in src and 'H85_COVER_CACHE_MAX = 256' in src)
ck('cover cache TTL is 90d','H85_COVER_CACHE_TTL_SEC = 90 * 24 * 60 * 60' in src)
ck('known accent preseed occurs before historical track apply',cover.find('_h12_cover_applied') < cover.find('_h85_record_loaded_track_pre('))
ck('unknown cover starts immediately after bind','_h16_cover_tick(panel)' in cover)
ck('cover cache validates hex colors','_h85_valid_cover_color' in load and '_h85_valid_cover_color' in write)
front,_=fn('_h85_global_filter'); card,_=fn('_h85_card_search_text'); stage,_=fn('_h85_sync_studio_stage')
ck('empty search has O1 repeat fast path',"_h85_search_empty_restored" in front and 'if not query:' in front)
ck('active search text is cached',"_h85_search_text_cache" in card and 'if key not in cache' in card)
ck('duplicate stage sync coalesced','H85_STAGE_COALESCE_MS' in stage and 'return' in stage)
ck('nav indicator shortened only','H85_NAV_INDICATOR_MS = 155' in src)
top,_=fn('_h85_set_topmost'); full,_=fn('_h85_foreground_fullscreen_on_lyric_monitor')
ck('topmost uses no-activate SetWindowPos','SetWindowPos' in top and '0x0010' in top)
ck('no input injection or focus steal','SetForegroundWindow' not in top and 'SendInput' not in src[src.find('# H85 resilient async'):])
ck('fullscreen check is same-monitor bounded','MonitorFromWindow' in full and 'fgmon!=ownmon' in full)
obs,_=fn('_h85_obs_tick'); paint,_=fn('_h85_lyric_paint'); obsinit,_=fn('_h85_obs_init')
ck('lyric repaint publishes frame serial','_h85_frame_serial' in paint)
ck('OBS target is ~30fps','H85_OBS_INTERVAL_MS = 33' in src and 'setInterval(H85_OBS_INTERVAL_MS)' in obsinit)
ck('OBS capture is dirty-aware','frame_changed' in obs and 'rect_changed' in obs and 'src.grab(rect)' in obs)
ck('OBS static frame skips grab','if frame_changed or rect_changed or mirror._frame.isNull()' in obs)
ck('OBS user-facing window hint present','LimbusLyric OBS Lyrics' in src[src.find('# H85 resilient async'):])
ck('H85 note present',(root/'RESILIENT_ASYNC_COVER_FULLSCREEN_FRONTEND_OBS_H85_NOTE_20260906.md').is_file())
print(f'H85 RESILIENT ASYNC/COVER/FULLSCREEN/FRONTEND/OBS: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
