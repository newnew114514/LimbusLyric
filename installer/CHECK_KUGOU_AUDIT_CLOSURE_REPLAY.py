from __future__ import annotations

import ast
import os
import queue
import sys
import textwrap
import time
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_KUGOU_AUDIT_CLOSURE_REPLAY.py <main.py>")

main_path = Path(sys.argv[1])
source = main_path.read_text(encoding="utf-8")
tree = ast.parse(source, filename=str(main_path))


def method(class_name: str, name: str) -> str:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == name:
                    return ast.get_source_segment(source, child)
    raise AssertionError(f"missing {class_name}.{name}")


def make_class(class_name: str, names: list[str], globals_dict):
    namespace = dict(globals_dict)
    body = "class %s:\n%s" % (
        class_name,
        "\n".join(textwrap.indent(method("MediaSessionSync", item), "    ") for item in names),
    )
    exec(body, namespace)
    namespace["MediaSessionSync"] = namespace[class_name]
    return namespace[class_name]


constants = {
    "time": time,
    "queue": queue,
    "write_error_log": lambda *args, **kwargs: None,
    "KUGOU_GESTURE_LEARNED_Y_TOLERANCE_PX": 14.0,
    "KUGOU_GESTURE_DRAG_MIN_PX": 18.0,
    "KUGOU_GESTURE_VERTICAL_MAX_PX": 36.0,
    "KUGOU_GESTURE_X_MIN": 0.025,
    "KUGOU_GESTURE_X_MAX": 0.975,
}


# This method is deliberately outside the 21 source-locked golden methods. It guards
# all existing golden callers without rewriting their down/move/up state machine.
ReplaySync = make_class(
    "ReplaySync",
    [
        "_kugou_target_from_cursor",
        "_kugou_guarded_target_from_cursor",
        "_kugou_consume_hooked_mouse_events",
        "_kugou_clear_inactive_mouse_events",
        "_kugou_hotpath_cached_window_rect",
        "_kugou_window_rect",
    ],
    {**constants, "os": os, "win32gui": None, "win32process": None},
)


def make_sync():
    sync = ReplaySync()
    sync._process_hint = "kgmusic"
    sync._process_stem = lambda value: str(value or "").split(".")[0].lower()
    sync._kugou_mouse_event_queue = queue.SimpleQueue()
    sync._kugou_deferred_mouse_events = []
    sync._kugou_physical_rect_cache = (0, 0, 1000, 600)
    class _HotReader:
        _kugou_last_main_rect = (0, 0, 1000, 600)
        def request_urgent_scan(self, *args, **kwargs): pass
    sync._uia_reader = _HotReader()
    sync._kugou_window_rect = lambda: (0, 0, 1000, 600)
    sync._kugou_visual_rail_bounds = (100.0, 900.0)
    sync._kugou_rail_y = 550.0
    sync._kugou_mouse_is_down = False
    sync._kugou_gesture_start = None
    sync._kugou_gesture_last = None
    sync._kugou_gesture_candidate = False
    sync._kugou_gesture_id = 0
    sync._kugou_mouse_event_last_diag_mono = 0.0
    sync._kugou_mouse_diag_last_mono = 0.0
    sync._kugou_host_v2_progress_last_success_mono = 0.0
    sync._kugou_host_v2_progress_trusted_key = ""
    sync._uia_duration_ms = 200000
    sync._state = {"duration_ms": 200000, "status": "playing"}
    sync._set_visual_seek_override = lambda *args, **kwargs: None
    sync.commits = []
    sync._kugou_commit_gesture_seek = lambda target, **kwargs: (
        sync.commits.append((target, kwargs)) or True
    ) if target is not None else False
    # Production installs the same outer guard once in __init__.
    sync._kugou_target_from_cursor = sync._kugou_guarded_target_from_cursor
    return sync


# Rail-outside same-Y click is not a seek.
sync = make_sync()
sync._kugou_mouse_event_queue.put((0x0201, 50, 550, 1000.0))
sync._kugou_mouse_event_queue.put((0x0202, 50, 550, 1040.0))
sync._kugou_consume_hooked_mouse_events()
assert sync.commits == [], sync.commits

# A deliberate in-rail horizontal drag still commits through the existing golden method.
sync = make_sync()
for event in (
    (0x0201, 250, 550, 2000.0),
    (0x0200, 520, 550, 2040.0),
    (0x0202, 520, 550, 2080.0),
):
    sync._kugou_mouse_event_queue.put(event)
sync._kugou_consume_hooked_mouse_events()
assert len(sync.commits) == 1 and 0 < sync.commits[0][0] < 200000, sync.commits

# A recently successful Host V2 RangeValue sample suppresses gesture fallback authority.
sync = make_sync()
sync._kugou_host_v2_progress_last_success_mono = time.monotonic() * 1000.0
sync._kugou_host_v2_progress_trusted_key = "uia-range:Slider:progress"
assert sync._kugou_guarded_target_from_cursor(500, (0, 0, 1000, 600)) is None

# The real Async wrapper exposes the two read-only delegates needed by _kugou_window_rect.
async_names = set()
for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == "AsyncPlayerUiPositionReader":
        async_names = {
            child.name for child in node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        break
assert {"_process_pids", "kugou_main_window_rect"} <= async_names, async_names

async_namespace = {"os": __import__("os"), "win32gui": None, "win32process": None}
exec(
    "class AsyncReplay:\n" +
    textwrap.indent(method("AsyncPlayerUiPositionReader", "_process_pids"), "    ") + "\n" +
    textwrap.indent(method("AsyncPlayerUiPositionReader", "kugou_main_window_rect"), "    "),
    async_namespace,
)
AsyncReplay = async_namespace["AsyncReplay"]

class Reader:
    def _process_pids(self, process_name):
        assert process_name == "kgmusic.exe"
        return {123, 456}

    def kugou_main_window_rect(self, process_name):
        assert process_name == "kgmusic.exe"
        return (10, 20, 1010, 720)


reader = AsyncReplay()
reader._reader = Reader()
reader._lock = __import__("threading").Lock()
assert reader._process_pids("kgmusic.exe") == {123, 456}
assert reader.kugou_main_window_rect("kgmusic.exe") == (10, 20, 1010, 720)

# Regression: the Windows KuGou branch must be pure Win32 and must never fall through
# to PlayerUiPositionReader._process_pids(), which shells out to tasklist synchronously.
process_source = method("AsyncPlayerUiPositionReader", "_process_pids")
rect_source = method("AsyncPlayerUiPositionReader", "kugou_main_window_rect")
assert "win32gui.EnumWindows" in process_source and "win32gui.EnumWindows" in rect_source
assert "subprocess.check_output" not in process_source and "[\'tasklist\'" not in process_source
assert "subprocess.check_output" not in rect_source and "[\'tasklist\'" not in rect_source

class FakePath:
    @staticmethod
    def basename(value):
        return str(value).replace("\\", "/").rsplit("/", 1)[-1]
class FakeOS:
    name = "nt"
    path = FakePath()
class FakeWin32Gui:
    @staticmethod
    def EnumWindows(cb, extra):
        cb(101, extra)
    @staticmethod
    def IsWindowVisible(hwnd): return True
    @staticmethod
    def IsIconic(hwnd): return False
    @staticmethod
    def GetClassName(hwnd): return "kugou_ui"
    @staticmethod
    def GetWindowText(hwnd): return "Artist - Song - 酷狗音乐"
    @staticmethod
    def GetWindowRect(hwnd): return (10, 20, 1010, 720)
class FakeWin32Process:
    @staticmethod
    def GetWindowThreadProcessId(hwnd): return (1, 456)

win_namespace = {
    "os": FakeOS(), "win32gui": FakeWin32Gui(), "win32process": FakeWin32Process(),
    "ctypes": __import__("ctypes"),
    "_kugou_host_candidate_score": lambda cls, title, rect, visible, iconic: 2000,
}
exec(
    "class AsyncWinReplay:\n" +
    textwrap.indent(process_source, "    ") + "\n" +
    textwrap.indent(rect_source, "    "),
    win_namespace,
)
AsyncWinReplay = win_namespace["AsyncWinReplay"]
class BlockingReader:
    _kugou_last_main_rect = None
    def _process_pids(self, process_name):
        raise AssertionError("KuGou GUI delegate fell through to synchronous tasklist path")
    def kugou_main_window_rect(self, process_name):
        raise AssertionError("KuGou GUI delegate fell through to synchronous legacy rect path")
win_reader = AsyncWinReplay()
win_reader._reader = BlockingReader()
win_reader._lock = __import__("threading").Lock()
assert win_reader._process_pids("kgmusic.exe") == {456}
assert win_reader.kugou_main_window_rect("kgmusic.exe") == (10, 20, 1010, 720)

# Execute the actual MediaSessionSync rect method through that Async wrapper. On this
# non-Windows replay the legacy Win32-only delegate is the expected selected rectangle.
rect_sync = ReplaySync()
rect_sync._uia_reader = reader
rect_sync._kugou_physical_rect_cache = None
rect_sync._kugou_physical_rect_cache_mono = 0.0
rect_sync._kugou_physical_rect_last_diag_mono = time.monotonic() * 1000.0
assert rect_sync._kugou_window_rect() == (10, 20, 1010, 720)

# Inactive global-hook events are discarded and the half-open gesture is reset. The
# existing hook callback remains lossless; lifecycle cleanup happens only outside it.
sync = make_sync()
sync._process_hint = "qqmusic"
sync._kugou_mouse_is_down = True
sync._kugou_gesture_start = (10, 20, 30.0, (0, 0, 1000, 600))
sync._kugou_gesture_candidate = True
for index in range(10000):
    sync._kugou_mouse_event_queue.put((0x0201 if index % 2 == 0 else 0x0202, index, 550, float(index)))
drained = sync._kugou_clear_inactive_mouse_events(reason="provider-inactive")
assert drained == 10000
assert sync._kugou_mouse_event_queue.empty()
assert not sync._kugou_mouse_is_down and sync._kugou_gesture_start is None and not sync._kugou_gesture_candidate
sync._process_hint = "kgmusic"
sync._kugou_consume_hooked_mouse_events()
assert sync.commits == []

init_source = method("MediaSessionSync", "__init__")
start_source = method("MediaSessionSync", "start")
snapshot_source = method("MediaSessionSync", "snapshot")
assert "self._kugou_target_from_cursor = self._kugou_guarded_target_from_cursor" in init_source
assert "self._kugou_clear_inactive_mouse_events" in start_source
assert "self._kugou_clear_inactive_mouse_events" in snapshot_source

print("KUGOU AUDIT CLOSURE REPLAY: PASS")
print("  Async PID/window-rect delegates are Win32-only on KuGou + real outer rect call: PASS")
print("  in-rail drag commits; rail-outside same-Y click rejected: PASS")
print("  healthy Host V2 RangeValue suppresses gesture fallback: PASS")
print("  inactive hook queue drained/reset; no historical seek on return: PASS")
