from __future__ import annotations
import ast
import sys
import time
from pathlib import Path

if len(sys.argv) != 2:
    print('usage: CHECK_WIN10_COMPATIBILITY_H23_REPLAY.py <main.py>')
    raise SystemExit(2)

main = Path(sys.argv[1]).resolve()
root = main.parent
source = main.read_text(encoding='utf-8')
fail = []

for token in (
    'WIN10 COMPATIBILITY + REPRO BUILD H23',
    'H23酷狗Win10无UIA初始化安全路径',
    'LIMBUSLYRIC_H23_KUGOU_WIN10_NO_UIA_INIT',
    'pywinauto-desktop=skip',
    'H23酷狗Win10 MSAA安全跳过',
    'H23酷狗Win10版本时长MSAA安全跳过',
):
    if token not in source:
        fail.append('missing H23 source token: ' + token)

tree = ast.parse(source, filename=str(main))
reader = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PlayerUiPositionReader'), None)
if reader is None:
    fail.append('PlayerUiPositionReader class missing')
else:
    methods = {n.name: n for n in reader.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    if '_kugou_win10_frozen_no_uia' not in methods:
        fail.append('H23 no-UIA compatibility predicate missing')
    poll = methods.get('poll')
    if poll is None:
        fail.append('PlayerUiPositionReader.poll missing')
    else:
        poll_src = ast.get_source_segment(source, poll) or ''
        safe_i = poll_src.find('kugou_win10_no_uia = bool(is_kugou and self._kugou_win10_frozen_no_uia())')
        desktop_i = poll_src.find('self._ensure_desktop()')
        if safe_i < 0 or desktop_i < 0 or safe_i >= desktop_i:
            fail.append('KuGou safe profile is not decided before UIA Desktop initialization')
        guarded = "if not kugou_win10_no_uia:\n            if not self._ensure_desktop():"
        if guarded not in poll_src:
            fail.append('UIA Desktop initialization is not fail-closed behind H23 compatibility guard')
        # The KuGou branch must return before the generic self._desktop.windows()/descendants lane.
        bounded_i = poll_src.find("'source': 'kugou-bounded-wait'")
        generic_i = poll_src.find('for w in self._desktop.windows()')
        if bounded_i < 0 or generic_i < 0 or bounded_i >= generic_i:
            fail.append('KuGou branch no longer exits before generic UIA full-tree scan')

core = (root / 'requirements_core.txt').read_text(encoding='utf-8').splitlines()
required_pins = {
    'PyQt5==5.15.11',
    'pywin32==311',
    'pywinauto==0.6.9',
    'comtypes==1.4.16',
}
missing = sorted(required_pins.difference(line.strip() for line in core))
if missing:
    fail.append('missing exact core runtime pin(s): ' + ', '.join(missing))
audio = (root / 'requirements_audio_emphasis_optional.txt').read_text(encoding='utf-8')
if 'pycaw==20251023' not in audio:
    fail.append('pycaw known-good runtime pin missing')

build = (root / 'installer' / 'BUILD_RELEASE.cmd').read_text(encoding='utf-8', errors='replace')
for token in (
    'py -3.12 -c',
    'Python 3.12.x',
    'VERIFY_BUILD_RUNTIME_PROFILE.py',
    'Existing build venv is not Python 3.12. Recreating it',
):
    if token not in build:
        fail.append('builder compatibility token missing: ' + token)

verify_path = root / 'installer' / 'VERIFY_BUILD_RUNTIME_PROFILE.py'
if not verify_path.is_file():
    fail.append('VERIFY_BUILD_RUNTIME_PROFILE.py missing')
else:
    verify = verify_path.read_text(encoding='utf-8')
    for token in ('"PyQt5": "5.15.11"', '"pywinauto": "0.6.9"', '"comtypes": "1.4.16"', '"pycaw": "20251023"', 'sys.version_info[:2] != (3, 12)'):
        if token not in verify:
            fail.append('runtime profile verifier missing: ' + token)

# Win10 frozen KuGou must also avoid the legacy comtypes/MSAA accessibility tree.
for token in (
    'PlayerUiPositionReader._try_kugou_msaa_probe = _h23_kugou_msaa_guard',
    'LyricFetcher.get_kugou_ui_duration_hint = staticmethod(_h23_kugou_duration_hint_guard)',
    'def _h23_kugou_win10_frozen_no_accessibility():',
):
    if token not in source:
        fail.append('H23 MSAA fail-closed token missing: ' + token)

# Execute the two H23 MSAA guards against throwing pre-calls: the exact safe profile must
# return before importing/traversing comtypes/oleacc code.
funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
try:
    ns = {
        'time': time,
        '_h23_kugou_win10_frozen_no_accessibility': lambda: True,
        '_h23_windows_build_number': lambda: 19045,
        'write_error_log': lambda *a, **k: None,
        '_LIMBUS_H23_KUGOU_MSAA_PRE': lambda *a, **k: (_ for _ in ()).throw(AssertionError('MSAA pre-call executed')),
        '_LIMBUS_H23_KUGOU_DURATION_HINT_PRE': lambda *a, **k: (_ for _ in ()).throw(AssertionError('duration MSAA pre-call executed')),
    }
    for name in ('_h23_kugou_msaa_guard', '_h23_kugou_duration_hint_guard'):
        if name not in funcs:
            fail.append('missing H23 guard function: ' + name)
        else:
            exec(ast.get_source_segment(source, funcs[name]), ns, ns)
    class Fake:
        pass
    if '_h23_kugou_msaa_guard' in ns and ns['_h23_kugou_msaa_guard'](Fake(), 'kgmusic.exe', {1}) is not None:
        fail.append('Win10 frozen MSAA clock guard did not fail closed')
    if '_h23_kugou_duration_hint_guard' in ns and ns['_h23_kugou_duration_hint_guard']({1}, 'song', 640) != 0:
        fail.append('Win10 frozen MSAA duration guard did not fail closed')
except Exception as exc:
    fail.append('H23 MSAA guard replay raised: ' + repr(exc))

# Defense-in-depth from H22 must remain installed even after the earlier H23 poll guard.
for token in (
    'MediaSessionSync._kugou_poll_uia_progress_v2 = _h22_kugou_progress_guard',
    'PlayerUiPositionReader._try_kugou_point_probe = _h22_kugou_point_probe_guard',
    'PlayerUiPositionReader._kugou_hidden_startup_range = _h22_kugou_hidden_range_guard',
    'AsyncPlayerUiPositionReader._kick_accessibility = _h22_kugou_accessibility_wake_guard',
):
    if token not in source:
        fail.append('H22 defense-in-depth lost: ' + token)

if fail:
    print('WIN10 COMPATIBILITY H23 REPLAY: FAIL')
    for item in fail:
        print(' -', item)
    raise SystemExit(1)

print('WIN10 COMPATIBILITY H23 REPLAY: PASS')
print(' - Win10 frozen KuGou decides no-UIA mode before Desktop(backend=uia) initialization')
print(' - KuGou bounded branch still exits before generic full-tree UIA scanning')
print(' - known-good direct COM/UI/runtime versions are pinned')
print(' - one-click builder deliberately selects/validates Python 3.12')
print(' - Win10 frozen KuGou also skips in-process comtypes/MSAA clock + version-tree scans')
print(' - H22 deep-probe/wake guards remain as defense-in-depth')
