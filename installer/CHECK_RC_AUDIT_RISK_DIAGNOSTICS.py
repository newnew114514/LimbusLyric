from __future__ import annotations

import ast
import math
import os
import sys
import textwrap
import threading
import time as real_time
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_RC_AUDIT_RISK_DIAGNOSTICS.py <main.py>")

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


def function(name: str) -> str:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(source, node)
    raise AssertionError(f"missing {name}")


class FakeTime:
    seconds = 0.0

    @classmethod
    def monotonic(cls):
        return float(cls.seconds)

    @classmethod
    def time(cls):
        return 1_800_000_000.0 + float(cls.seconds)


logs = []
common_log = lambda *args, **kwargs: logs.append((args, kwargs))


# 1) NetEase: execute the production transition method without changing it.
ncm_globals = {
    "NETEASE_NATIVE_LOG_ENABLED": True,
    "time": FakeTime,
    "math": math,
    "_clean_name": lambda value: str(value or "").strip().lower(),
    "write_error_log": common_log,
}
ncm_code = textwrap.dedent(method("MediaSessionSync", "_poll_netease_native_clock")).replace(
    "def _poll_netease_native_clock", "def replay_ncm", 1
)
exec(ncm_code, ncm_globals)


class NativeFeed:
    def __init__(self):
        self.snap = {}

    def start_background(self):
        return None

    def snapshot(self):
        return dict(self.snap)


class Ncm:
    pass


ncm = Ncm()
ncm._netease_native = NativeFeed()
ncm._process_hint = "cloudmusic"
ncm._process_stem = lambda value: str(value or "").split(".")[0]
ncm._netease_native_primary = False
ncm._netease_native_last_diag_mono = 0.0
ncm._netease_native_last_position_ms = None
ncm._netease_native_last_mono = 0.0
ncm._netease_native_last_track_key = ""
ncm._netease_native_last_track_serial = -1
ncm._netease_native_transition_pending = False
ncm._netease_native_transition_old_position_ms = None
ncm._netease_native_transition_started_mono = 0.0
ncm._netease_native_seek_guard_until_mono = 0.0
ncm._netease_native_last_seek_serial = 0
ncm._uia_duration_ms = 300000
ncm._mark_seek_burst = lambda *args, **kwargs: None
ncm._track_key = "old|artist"
ncm._netease_native.snap = {
    "ready": True,
    "position_ms": 240000,
    "duration_ms": 300000,
    "title": "old",
    "artist": "artist",
    "status": "playing",
    "track_serial": 1,
    "seek_serial": 1,
}
FakeTime.seconds = 0.0
ncm_globals["replay_ncm"](ncm, "playing")
ncm._track_key = "new|artist"
ncm._netease_native.snap.update({"title": "new", "track_serial": 2})
FakeTime.seconds = 0.1
pending = ncm_globals["replay_ncm"](ncm, "playing")
assert pending["clock_ok"] is False and ncm._netease_native_primary is False
FakeTime.seconds = 1.8
after_timeout = ncm_globals["replay_ncm"](ncm, "playing")
ncm_risk_reproduced = bool(after_timeout["clock_ok"] and ncm._netease_native_primary)
assert ncm_risk_reproduced


# 2) QQ: prove the same-duration stale GSMTC sample can arm the existing position veto.
qq_update_globals = {
    "time": FakeTime,
    "QQ_GSMTC_IDENTITY_GUARD_ENABLED": True,
    "QQ_GSMTC_IDENTITY_DURATION_TOLERANCE_MIN_MS": 1800.0,
    "QQ_GSMTC_IDENTITY_DURATION_TOLERANCE_RATIO": 0.015,
    "QQ_GSMTC_IDENTITY_SEEK_CONFIRM_MAX_GAP_MS": 1400.0,
    "write_error_log": common_log,
}
qq_update_code = textwrap.dedent(method("MediaSessionSync", "_qq_update_gsmtc_identity_guard")).replace(
    "def _qq_update_gsmtc_identity_guard", "def replay_qq_update", 1
)
exec(qq_update_code, qq_update_globals)


class QqSync:
    pass


qq = QqSync()
qq._uia_duration_ms = 220500
qq._qq_gsmtc_identity_guard_active = False
qq._qq_gsmtc_identity_duration_ms = None
qq._qq_gsmtc_identity_seek_pending = None
qq._qq_gsmtc_identity_seek_confirmed_mono = 0.0
qq._qq_gsmtc_identity_seek_confirmed_start_mono = 0.0
qq._qq_gsmtc_identity_seek_confirmed_position_ms = None
qq._qq_gsmtc_identity_last_position_ms = None
qq._qq_gsmtc_identity_last_mono = None
qq._qq_gsmtc_identity_last_diag_mono = 0.0
qq._qq_gsmtc_last_position_ms = None
qq._qq_gsmtc_last_mono = None
qq._qq_gsmtc_good_streak = 0
qq._qq_gsmtc_primary = False
FakeTime.seconds = 10.0
assert qq_update_globals["replay_qq_update"](qq, 180000, True, "playing", 221000) is True

guard_globals = {
    "time": FakeTime,
    "QQ_GSMTC_IDENTITY_DURATION_TOLERANCE_MIN_MS": 1800.0,
    "QQ_GSMTC_IDENTITY_DURATION_TOLERANCE_RATIO": 0.015,
    "QQ_DIRECT_GSMTC_POSITION_VETO_MIN_DELTA_MS": 4200.0,
    "QQ_GSMTC_IDENTITY_UIA_REACQUIRE_COOLDOWN_MS": 2600.0,
    "write_error_log": common_log,
}
exec(
    "class Guard:\n" +
    textwrap.indent(method("AsyncPlayerUiPositionReader", "set_qq_gsmtc_identity_guard"), "    ") + "\n" +
    textwrap.indent(method("AsyncPlayerUiPositionReader", "_guard_qq_duration_mismatch_result"), "    "),
    guard_globals,
)
guard = guard_globals["Guard"]()
guard._lock = threading.Lock()
guard._qq_gsmtc_identity_guard = {}
guard._qq_gsmtc_guard_last_diag_mono = 0.0
guard._qq_gsmtc_guard_last_reacquire_mono = 0.0
guard.set_qq_gsmtc_identity_guard(True, 220500, 221000, 180000, position_veto=True)
uia_b = {
    "position_ms": 2000,
    "duration_ms": 220500,
    "confidence": 168,
    "source": "qq-time-pair-validated",
    "source_key": "pair-b",
}
guarded = guard._guard_qq_duration_mismatch_result(None, "qqmusic.exe", uia_b)
qq_risk_reproduced = guarded.get("source") == "qq-gsmtc-veto-uia-position" and guarded.get("position_ms") is None
assert qq_risk_reproduced


# 3) Retired UIA generations: use the production spawn/invalidate methods with a fake
# permanently blocking poll lane, then separately execute the old-generation publish guard.
retired_globals = {"threading": threading, "time": real_time}
exec(
    "class Retired:\n" +
    textwrap.indent(method("AsyncPlayerUiPositionReader", "_spawn_generation_worker"), "    ") + "\n" +
    textwrap.indent(method("AsyncPlayerUiPositionReader", "invalidate_sample"), "    "),
    retired_globals,
)
retired = retired_globals["Retired"]()
retired._lock = threading.Lock()
retired._thread = None
retired._retired_threads = []
retired._process_name = "cloudmusic.exe"
retired._generation = 0
retired._clock_lane_epoch = 0
retired._clock_hint = None
retired._clock_last_sample_mono = 0.0
retired._progress_wake_process_started_mono = 0.0
retired._progress_wake_requested_mono = 0.0
retired._progress_wake_baseline_position_ms = None
retired._lyric_clock_window_until_mono = 0.0
retired._suspended = False
retired._stop_event = threading.Event()
retired._block = threading.Event()
retired._readers = []
retired._start_accessibility_wake = lambda *_args: None


class RetiredReader:
    _diagnostics_enabled = True


def make_reader():
    reader = RetiredReader()
    retired._readers.append(reader)
    return reader


retired._make_reader = make_reader
retired._reader = make_reader()
retired._worker_main = lambda *_args: retired._block.wait()
retired._spawn_generation_worker(retired._process_name, 0, retired._reader)
for _index in range(8):
    retired.invalidate_sample()
live_retired = sum(1 for item in retired._retired_threads if item.is_alive())
reader_objects = len(retired._readers)
assert live_retired == 8 and reader_objects == 9, (live_retired, reader_objects)

worker_globals = {"threading": threading, "time": real_time, "os": os, "write_error_log": common_log}
exec("class Worker:\n" + textwrap.indent(method("AsyncPlayerUiPositionReader", "_worker_main"), "    "), worker_globals)
worker = worker_globals["Worker"]()
worker._lock = threading.Lock()
worker._stop_event = threading.Event()
worker._generation = 1
worker._process_name = "dummy.exe"
worker._qq_track_epoch = 0
worker._qq_reacquire_epoch = 0
worker._suspended = False
worker._cached = {"source": "initial"}
entered = threading.Event()
release = threading.Event()


class BlockingReader:
    def poll(self, *_args, **_kwargs):
        entered.set()
        release.wait(2.0)
        return {"position_ms": 999999, "source": "old-generation"}


thread = threading.Thread(target=worker._worker_main, args=(1, "dummy.exe", BlockingReader()), daemon=True)
thread.start()
assert entered.wait(2.0)
with worker._lock:
    worker._generation = 2
release.set()
thread.join(2.0)
old_generation_published = worker._cached.get("source") == "old-generation"
assert not old_generation_published


# 4) Text-boundary sparse cadence: execute the real helper at 1.2-1.6s intervals.
text_globals = {
    "QQ_TEXT_BOUNDARY_PHASE_PRIOR_MS": 420.0,
    "QQ_TEXT_BOUNDARY_MAX_BRACKET_MS": 1050.0,
    "QQ_TEXT_BOUNDARY_MAX_CADENCE_ERROR_MS": 440.0,
    "QQ_TEXT_BOUNDARY_MAX_SPREAD_MS": 380.0,
    "QQ_TEXT_BOUNDARY_MIN_EDGES": 2,
    "QQ_TEXT_BOUNDARY_WINDOW": 6,
    "QQ_PHASE_EDGE_MIN_STEP_MS": 700.0,
    "QQ_PHASE_EDGE_MAX_STEP_MS": 1300.0,
}
exec(function("_qq_text_boundary_clock_step"), text_globals)
step = text_globals["_qq_text_boundary_clock_step"]
state = None
ready_samples = []
diagnostics = []
for raw, now in ((0, 0), (1000, 1200), (2000, 2800), (3000, 4000), (4000, 5600)):
    state, candidate, ready, diag = step(state, raw, now, "qq-text")
    ready_samples.append(bool(ready))
    diagnostics.append(diag)
sparse_never_ready = not any(ready_samples)
assert sparse_never_ready and all(item.get("reason") == "epoch-reset" for item in diagnostics[1:])


print("RC AUDIT RISK DIAGNOSTICS: PASS")
print(f"  netease_stale_timeout_regrants_primary={int(ncm_risk_reproduced)}")
print(f"  qq_same_duration_stale_gsmtc_vetoes_new_uia={int(qq_risk_reproduced)}")
print(f"  retired_live_threads={live_retired} reader_objects={reader_objects} old_generation_published={int(old_generation_published)}")
print(f"  qq_text_sparse_boundary_ready={int(not sparse_never_ready)} phase_prior_ms=420")
