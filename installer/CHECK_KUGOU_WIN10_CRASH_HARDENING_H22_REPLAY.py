from __future__ import annotations
import ast, sys, time
from pathlib import Path

if len(sys.argv) != 2:
    print('usage: CHECK_KUGOU_WIN10_CRASH_HARDENING_H22_REPLAY.py <main.py>')
    raise SystemExit(2)

main = Path(sys.argv[1]).resolve()
source = main.read_text(encoding='utf-8')
fail = []

for token in (
    'KUGOU WIN10 CRASH HARDENING H22',
    'H22酷狗HostV2 UIA安全模式',
    'H22酷狗HostV2 UIA熔断',
    'H22原生崩溃追踪',
    'faulthandler.enable(file=handle, all_threads=True)',
    'MediaSessionSync._kugou_poll_uia_progress_v2 = _h22_kugou_progress_guard',
    'PlayerUiPositionReader._try_kugou_point_probe = _h22_kugou_point_probe_guard',
    'PlayerUiPositionReader._kugou_hidden_startup_range = _h22_kugou_hidden_range_guard',
    'AsyncPlayerUiPositionReader._kick_accessibility = _h22_kugou_accessibility_wake_guard',
    "LIMBUSLYRIC_KUGOU_HOST_V2_UIA_WIN10",
):
    if token not in source:
        fail.append('missing source token: ' + token)

tree = ast.parse(source, filename=str(main))
funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
for name in ('_h22_windows_build_number', '_h22_kugou_win10_frozen_safe_mode', '_h22_kugou_progress_guard', '_h22_kugou_point_probe_guard', '_h22_kugou_hidden_range_guard', '_h22_kugou_accessibility_wake_guard', '_h22_enable_native_fault_trace'):
    if name not in funcs:
        fail.append('missing function: ' + name)

# Execute only the H22 guard function against stubs. This avoids importing PyQt/Windows APIs.
if '_h22_kugou_progress_guard' in funcs:
    fn_src = ast.get_source_segment(source, funcs['_h22_kugou_progress_guard'])
    ns = {'time': time}
    exec(fn_src, ns, ns)
    guard = ns['_h22_kugou_progress_guard']

    class Fake:
        def __init__(self):
            self.calls = 0
        def _kugou_resolve_host_v2(self):
            return {'hwnd': 1234}

    # Exact field safety mode: the risky pre-call must never execute.
    fake = Fake()
    ns['_h22_kugou_win10_frozen_safe_mode'] = lambda: True
    ns['_h22_windows_build_number'] = lambda: 19045
    ns['write_error_log'] = lambda *a, **k: None
    ns['_LIMBUS_H22_KUGOU_PROGRESS_PRE'] = lambda *a, **k: (_ for _ in ()).throw(AssertionError('pre-call executed in Win10 frozen safe mode'))
    ns['H22_KUGOU_HOST_UIA_SLOW_MS'] = 1500.0
    ns['H22_KUGOU_HOST_UIA_SLOW_FUSE_SEC'] = 300.0
    ns['H22_KUGOU_HOST_UIA_MISS_FUSE_SEC'] = 90.0
    ns['H22_KUGOU_HOST_UIA_MISS_LIMIT'] = 3
    try:
        out = guard(fake, 'playing', 0)
        if out is not None:
            fail.append('Win10 frozen safe mode did not fail closed')
    except Exception as exc:
        fail.append('Win10 frozen safe mode raised: ' + repr(exc))

    # Non-safe-mode slow provider: first call may finish, but it must arm a fuse and the
    # immediate second call must not re-enter the provider.
    fake = Fake()
    ns['_h22_kugou_win10_frozen_safe_mode'] = lambda: False
    counter = {'n': 0}
    def slow_pre(self, status, local_position_hint=None):
        counter['n'] += 1
        return None
    ns['_LIMBUS_H22_KUGOU_PROGRESS_PRE'] = slow_pre
    # Deterministically exercise the slow-provider branch.  Older replay revisions used
    # sleep(12ms) against a 5ms threshold; on some Windows/VM timer configurations that
    # synthetic delay can be observed below the threshold, producing a false release failure
    # even though the H33F1 mandatory next-call barrier is present.  A zero threshold tests
    # the branch contract directly and leaves the production H22 threshold untouched.
    ns['H22_KUGOU_HOST_UIA_SLOW_MS'] = 0.0
    ns['H22_KUGOU_HOST_UIA_SLOW_FUSE_SEC'] = 30.0
    try:
        guard(fake, 'playing', 0)
        guard(fake, 'playing', 0)
        if counter['n'] != 1:
            fail.append(f'slow-provider fuse did not suppress second call: calls={counter["n"]}')
        if float(getattr(fake, '_h22_kugou_host_uia_fused_until_mono', 0.0) or 0.0) <= time.monotonic():
            fail.append('slow-provider fuse deadline not armed')
    except Exception as exc:
        fail.append('slow-provider replay raised: ' + repr(exc))

    # Quick repeated no-range misses must also fuse, preventing endless harmless-but-expensive scans.
    fake = Fake()
    counter = {'n': 0}
    def miss_pre(self, status, local_position_hint=None):
        counter['n'] += 1
        return None
    ns['_LIMBUS_H22_KUGOU_PROGRESS_PRE'] = miss_pre
    ns['H22_KUGOU_HOST_UIA_SLOW_MS'] = 999999.0
    ns['H22_KUGOU_HOST_UIA_MISS_LIMIT'] = 3
    ns['H22_KUGOU_HOST_UIA_MISS_FUSE_SEC'] = 30.0
    try:
        guard(fake, 'playing', 0)
        guard(fake, 'playing', 0)
        guard(fake, 'playing', 0)
        guard(fake, 'playing', 0)
        if counter['n'] != 3:
            fail.append(f'miss fuse did not suppress fourth call: calls={counter["n"]}')
    except Exception as exc:
        fail.append('miss-fuse replay raised: ' + repr(exc))

# The other three KuGou UIA entry points must also fail closed in the exact field environment.
try:
    guard_ns = {
        '_h22_kugou_win10_frozen_safe_mode': lambda: True,
        '_h22_windows_build_number': lambda: 19045,
        'write_error_log': lambda *a, **k: None,
        '_LIMBUS_H22_KUGOU_POINT_PRE': lambda *a, **k: (_ for _ in ()).throw(AssertionError('point probe executed')),
        '_LIMBUS_H22_KUGOU_HIDDEN_RANGE_PRE': lambda *a, **k: (_ for _ in ()).throw(AssertionError('hidden range executed')),
        '_LIMBUS_H22_KUGOU_WAKE_PRE': lambda *a, **k: (_ for _ in ()).throw(AssertionError('wake executed')),
    }
    for name in ('_h22_kugou_point_probe_guard','_h22_kugou_hidden_range_guard','_h22_kugou_accessibility_wake_guard'):
        exec(ast.get_source_segment(source, funcs[name]), guard_ns, guard_ns)
    dummy = object()
    if guard_ns['_h22_kugou_point_probe_guard'](dummy, 'kgmusic.exe', {1}) is not None:
        fail.append('Win10 point-probe guard did not return None')
    if guard_ns['_h22_kugou_hidden_range_guard'](dummy, 'kgmusic.exe', {1}) is not None:
        fail.append('Win10 hidden-range guard did not return None')
    if guard_ns['_h22_kugou_accessibility_wake_guard'](dummy, 'kgmusic.exe') is not None:
        fail.append('Win10 accessibility-wake guard did not return None')
except Exception as exc:
    fail.append('Win10 secondary UIA guard replay raised: ' + repr(exc))

if fail:
    print('KUGOU WIN10 CRASH HARDENING H22 REPLAY: FAIL')
    for item in fail:
        print(' -', item)
    raise SystemExit(1)

print('KUGOU WIN10 CRASH HARDENING H22 REPLAY: PASS')
print(' - Win10 frozen: in-process HostV2 deep UIA Range scan is fail-closed')
print(' - slow provider: one completed slow call arms a long fuse')
print(' - repeated no-range provider: miss fuse prevents endless re-entry')
print(' - Win10 frozen: hidden-range / dense point-probe / shallow pywinauto wake are also suppressed')
print(' - native fault trace wiring present')
