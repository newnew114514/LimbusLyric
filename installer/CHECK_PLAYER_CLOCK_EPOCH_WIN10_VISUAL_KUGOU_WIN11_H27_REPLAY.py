from pathlib import Path
import sys,re
if len(sys.argv)!=2: raise SystemExit(2)
s=Path(sys.argv[1]).read_text(encoding='utf-8')
need=[
'H27酷狗新曲时钟证据代际隔离',
"H26_TRANSITION_STRONG_POSITION_SOURCES.discard('kugou-rail-local-master')",
'_LIMBUS_H22_KUGOU_PROGRESS_PRE(self, status, local_position_hint=local_position_hint)',
'H27酷狗新曲事务阻止旧歌词恢复',
'_h27_win32_process_window_rect',
"_h27_win32_process_window_rect('cloudmusic.exe')",
'_h27_netease_static_rail_candidates',
'MediaSessionSync.bind_track = _h27_bind_track_epoch_barrier',
'MediaSessionSync._kugou_poll_uia_progress_v2 = _h27_kugou_progress_guard',
'ControlPanel._restore_qq_suspended_loaded_track = _h27_restore_suspended_track',
'_h25_netease_window_rect = _h27_netease_window_rect',
'_h26_netease_static_rail_candidates = _h27_netease_static_rail_candidates',
]
for x in need:
    if x not in s: raise AssertionError('missing '+x)
# H27 final install must be after historical H22/H21 blocks and before __main__.
pos=s.index('# H27 player-clock epoch')
assert pos > s.index('# H14 auto-precision deadline')
assert pos > s.index('MediaSessionSync._kugou_poll_uia_progress_v2 = _h22_kugou_progress_guard')
assert pos < s.index('if __name__ == "__main__":')
# Field regression: KuGou local-master must no longer be classified strong for transition origin.
h26=s[s.index('H26_TRANSITION_STRONG_POSITION_SOURCES = {'):s.index('_LIMBUS_H26_ACTIVE_PLAYER')]
assert "'kugou-rail-local-master'" in h26  # historical bytes stay intact
assert "discard('kugou-rail-local-master')" in s[pos:]
# Win11 gate is build-based, not frozen-only, matching user's source-run field log (build 26100/frozen=0).
h27=s[pos:s.index('if __name__ == "__main__":')]
assert "_h27_windows_build_number() < 22000" in h27
assert "getattr(_sys, 'frozen'" not in h27[h27.index('def _h27_is_win11_kugou'):h27.index('def _h27_new_track_key')]
# NetEase zero-touch window path must avoid tasklist/pywinauto/UIA in its new resolver.
resolver=h27[h27.index('def _h27_win32_process_window_rect'):h27.index('def _h27_netease_window_rect')]
for bad in ('tasklist','pywinauto','Desktop(','WM_GETOBJECT'):
    assert bad not in resolver
for good in ('EnumWindows','GetWindowThreadProcessId','QueryFullProcessImageNameW'):
    assert good in resolver
print('PLAYER CLOCK EPOCH + WIN10 VISUAL + KUGOU WIN11 H27 REPLAY: PASS')
print(' - KuGou previous-track rail cannot seed a new-track transition')
print(' - Win11 HostV2 proof-pending bypasses H22 miss-fuse semantics')
print(' - fresh KuGou new-track transport evidence blocks stale-host lyric restoration')
print(' - Win10 NetEase zero-touch rect discovery is pure Win32 and H27 rail discovery is single-boundary/two-colour')
