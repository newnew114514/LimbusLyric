#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys, time, types
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_QQ_AUTOTRACK_ROLLBACK_GUARD_H95F10F5_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ QQ AUTOTRACK ROLLBACK GUARD H95F10F5' in src,'H95F10F5 build tag missing')
marker='# H95F10F5 QQ auto-track rollback guard'
need(marker in src,'H95F10F5 runtime marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
for name in ('_h95f10f5_should_block_qq_old_restore','_h95f10f5_restore_suspended_loaded_track','_h95f10f5_activate'):
    need(name in funcs,'H95F10F5 function missing: '+name)
_s=src.index(marker)
block=src[_s:src.index('# H95F10F6 bilingual optical blur parity + precise recovery + sync UI cleanup',_s)]
for token in (
    'H95F10F5_QQ_IDENTITY_ROLLBACK_GUARD_MS = 2600.0',
    "hint_key != target",
    "requested != loaded",
    "ControlPanel._restore_qq_suspended_loaded_track = _h95f10f5_restore_suspended_loaded_track",
    'H95F10F5 QQ新曲事务阻止旧歌词回滚',
    'transport/search=unchanged',
): need(token in block,'H95F10F5 invariant missing: '+token)
for bad in ('MediaSessionSync.position =','MediaSessionSync.seek =','MediaSessionSync.bind_track =','ControlPanel._request_auto_track =','ControlPanel._monitor_track_change =','LyricSearchEngine.search ='):
    need(bad not in block,'H95F10F5 crossed protected authority: '+bad)

# Execute the exact old-field race predicate: fresh new fast-event owns target, detector briefly
# returns the still-loaded old title.  It must be blocked only inside the short publication lag.
nodes=[]
for name in ('_h95f10f5_should_block_qq_old_restore','_h95f10f5_restore_suspended_loaded_track'):
    node=copy.deepcopy(funcs[name]); node.decorator_list=[]; nodes.append(node)
pre_calls=[]
ns={
    'time':time,
    'H95F10F5_QQ_IDENTITY_ROLLBACK_GUARD_MS':2600.0,
    '_H95F10F5_RESTORE_PRE':lambda panel,song,artist='': pre_calls.append((song,artist)) or 'delegated',
    'write_error_log':lambda *a,**k:None,
}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<h95f10f5>','exec'),ns)
class Combo:
    def __init__(self,v): self.v=v
    def currentText(self): return self.v
class Panel:
    def __init__(self):
        self.player_combo=Combo('QQ音乐')
        self._auto_overlay_suspended=True
        self._auto_target_key='mede:mede|reolれをる'
        self._loaded_track_key='floweroflife|陽花'
        self._qq_background_hint_key=self._auto_target_key
        self._qq_background_hint_log_mono=100.0
    def _track_identity(self,song,artist=''):
        return f'{str(song).replace(" ","").lower()}|{artist}'
panel=Panel(); pred=ns['_h95f10f5_should_block_qq_old_restore']
need(pred(panel,'Flower of Life','陽花',now_mono=101.0) is True,'fresh new QQ target did not block stale loaded-track restore')
need(pred(panel,'Flower of Life','陽花',now_mono=102.601) is False,'rollback guard did not expire for genuine return')
need(pred(panel,'mede:mede','reolれをる',now_mono=101.0) is False,'new target itself was incorrectly blocked')
panel._qq_background_hint_key='other|x'
need(pred(panel,'Flower of Life','陽花',now_mono=101.0) is False,'unrelated QQ hint blocked restore')
panel._qq_background_hint_key=panel._auto_target_key; panel.player_combo=Combo('网易云音乐')
need(pred(panel,'Flower of Life','陽花',now_mono=101.0) is False,'QQ-only guard leaked to another player')
panel.player_combo=Combo('QQ音乐'); panel._auto_overlay_suspended=False
need(pred(panel,'Flower of Life','陽花',now_mono=101.0) is False,'non-suspended old payload was blocked')

# Final wrapper must not delegate during the exact race, but must delegate after expiry.
panel._auto_overlay_suspended=True; panel._qq_background_hint_log_mono=time.monotonic()-1.0
pre_calls.clear(); out=ns['_h95f10f5_restore_suspended_loaded_track'](panel,'Flower of Life','陽花')
need(out is False and not pre_calls,'fresh stale-old restore delegated to historical recovery path')
panel._qq_background_hint_log_mono=time.monotonic()-3.0
out=ns['_h95f10f5_restore_suspended_loaded_track'](panel,'Flower of Life','陽花')
need(out=='delegated' and len(pre_calls)==1,'expired/genuine old-track restore no longer delegates')
print('QQ AUTOTRACK ROLLBACK GUARD H95F10F5 REPLAY: PASS')
print('  fresh fast-event target blocks stale old snapshot restore: PASS')
print('  guard expires and genuine return still restores cached lyrics: PASS')
print('  search/clock/detector authority untouched: PASS')
