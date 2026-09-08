#!/usr/bin/env python3
import ast
import os
import sys
import textwrap
import time
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_ALL_PLAYER_LATE_ATTACH_PLAYER_SCOPE_REPLAY.py <main.py>")

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")
tree = ast.parse(source)


def fail(message):
    print("ALL PLAYER LATE-ATTACH PLAYER-SCOPE REPLAY: FAIL")
    print("  -", message)
    raise SystemExit(1)


def function_source(class_name, function_name):
    lines = source.splitlines(True)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == function_name:
                    return textwrap.dedent("".join(lines[child.lineno - 1:child.end_lineno]))
    fail(f"missing {class_name}.{function_name}")


arm_source = function_source("ControlPanel", "_arm_zero_touch_selected_player")
request_source = function_source("ControlPanel", "_request_auto_track")
active_target_source = function_source("ControlPanel", "_active_auto_target_matches")


class QTimer:
    @staticmethod
    def singleShot(_delay, _callback):
        return None


namespace = {
    "BUILTIN_ZERO_TOUCH_BOOTSTRAP_ENABLED": True,
    "NETEASE_INTERNAL_BRIDGE_ENABLED": True,
    "SOURCE_GUARD_ENABLED": True,
    "QTimer": QTimer,
    "os": os,
    "time": time,
    "write_error_log": lambda *_args, **_kwargs: None,
}
exec(
    "class Harness:\n"
    + textwrap.indent(arm_source, "    ")
    + textwrap.indent(active_target_source, "    ")
    + textwrap.indent(request_source, "    "),
    namespace,
)
Harness = namespace["Harness"]


class Value:
    def __init__(self, value):
        self.value = value

    def currentText(self):
        return self.value

    def isChecked(self):
        return bool(self.value)


class Signal:
    def connect(self, _callback):
        return None


class Reader:
    def poll(self, _process_name):
        return {}


class MediaSync:
    def __init__(self):
        self.started = []
        self.binds = []
        self._uia_reader = Reader()

    def start(self, process_name):
        self.started.append(process_name)

    def bind_track(self, song, artist, duration, **kwargs):
        self.binds.append((song, artist, duration, dict(kwargs)))

    def _netease_bridge_transport_sample(self, **_kwargs):
        return {}


class LyricWindow:
    def stop_lyric(self):
        return None


class TextInput:
    def toPlainText(self):
        return "cached old lyrics"


class Status:
    def setText(self, _text):
        return None


def make_harness(selected_player, loaded_player, loaded_key, lyric_source):
    harness = Harness()
    harness._is_started = False
    harness._auto_armed = False
    harness._zero_touch_armed = False
    harness._zero_touch_player = ""
    harness._zero_touch_first_attach_pending = False
    harness._loaded_player = loaded_player
    harness._loaded_track_key = loaded_key
    harness._loaded_song = "old song" if loaded_key else ""
    harness._loaded_artist = "old artist" if loaded_key else ""
    harness._auto_candidate_since = time.monotonic() - 2.0
    harness._auto_candidate_key = "candidate"
    harness._auto_candidate_hits = 2
    harness._auto_target_key = ""
    harness._auto_generation = 0
    harness._auto_fetch_in_progress = False
    harness._auto_queued_job = None
    harness._qq_auto_txn_slot_connected = False
    harness._auto_overlay_suspended = False
    harness._auto_suspended_loaded_key = ""
    harness.players = {
        "QQ音乐": {"process": "qqmusic.exe"},
        "网易云音乐": {"process": "cloudmusic.exe"},
        "酷狗音乐": {"process": "kgmusic.exe"},
    }
    harness.player_combo = Value(selected_player)
    harness.source_combo = Value(lyric_source)
    harness.auto_track_check = Value(True)
    harness.trans_check = Value(False)
    harness.precise_tracking_check = Value(True)
    harness.media_sync = MediaSync()
    harness.lyric_window = LyricWindow()
    harness.text_input = TextInput()
    harness.status = Status()
    harness.auto_lyric_result = Signal()
    harness._on_qq_auto_lyric_transaction_result = lambda *_args: None
    harness._monitor_track_change = lambda: None
    harness._same_track = lambda a, b, c, d: (a.strip().lower(), b.strip().lower()) == (c.strip().lower(), d.strip().lower())
    harness._track_identity = lambda song, artist="": f"{song.strip().lower()}|{artist.strip().lower()}"
    harness.jobs = []
    harness._start_auto_search_job = lambda job: harness.jobs.append(dict(job))
    return harness


def run_case(selected_player, loaded_player, loaded_key, lyric_source, expect_late_attach):
    harness = make_harness(selected_player, loaded_player, loaded_key, lyric_source)
    harness._arm_zero_touch_selected_player()
    if bool(harness._zero_touch_first_attach_pending) != bool(expect_late_attach):
        fail(
            f"arm scope wrong: loaded_player={loaded_player or '<none>'}, "
            f"selected_player={selected_player}, lyric_source={lyric_source}, "
            f"pending={int(bool(harness._zero_touch_first_attach_pending))}"
        )
    harness._request_auto_track("new song", "new artist")
    if len(harness.media_sync.binds) != 1 or len(harness.jobs) != 1:
        fail(f"request did not produce exactly one bind/job for {loaded_player}->{selected_player}")
    bind = harness.media_sync.binds[0]
    kwargs = bind[3]
    job = harness.jobs[0]
    if bool(kwargs.get("startup_existing")) != bool(expect_late_attach):
        fail(f"bind startup_existing wrong for {loaded_player}->{selected_player}: {kwargs}")
    if bool(job.get("startup_existing_attach")) != bool(expect_late_attach):
        fail(f"job startup_existing_attach wrong for {loaded_player}->{selected_player}: {job}")
    if expect_late_attach and int(kwargs.get("initial_position_ms") or 0) != 0:
        fail(f"late attach leaked detection latency for {loaded_player}->{selected_player}: {kwargs}")
    if not expect_late_attach and int(kwargs.get("initial_position_ms") or 0) < 1000:
        fail(f"same-player normal transition lost historical detection-latency behavior: {kwargs}")


# Fresh launch and every cross-player switch are first attaches for the selected transport,
# regardless of which lyric provider is selected.
run_case("QQ音乐", "", "", "网易云", True)
run_case("酷狗音乐", "QQ音乐", "old|qq", "网易云", True)
run_case("QQ音乐", "酷狗音乐", "old|kg", "网易云", True)
run_case("酷狗音乐", "网易云音乐", "old|ncm", "QQ音乐", True)

# Negative control: an already-loaded track from the same actual player is not a cross-player
# first attach. Its ordinary track-change bootstrap remains unchanged.
run_case("QQ音乐", "QQ音乐", "old|qq", "网易云", False)

print("ALL PLAYER LATE-ATTACH PLAYER-SCOPE REPLAY: PASS")
print("  fresh launch + cross-player first attach are scoped by actual player, not lyric source: PASS")
print("  cross-player bind suppresses detection-latency/song-zero bootstrap: PASS")
print("  same-player ordinary track transition remains unchanged: PASS")
