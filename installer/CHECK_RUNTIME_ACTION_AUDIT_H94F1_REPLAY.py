#!/usr/bin/env python3
from __future__ import annotations

import ast
import ctypes
import pathlib
import sys
import threading
from types import SimpleNamespace as NS

if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_RUNTIME_ACTION_AUDIT_H94F1_REPLAY.py <main.py>")

source = pathlib.Path(sys.argv[1]).resolve()
text = source.read_text(encoding="utf-8")
tree = ast.parse(text)
nodes = {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
imports = {
    a.asname or a.name
    for n in tree.body
    if isinstance(n, ast.ImportFrom)
    for a in n.names
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def function(name, env):
    node = nodes.get(name)
    need(node is not None, f"function missing: {name}")
    node = ast.fix_missing_locations(ast.parse(ast.unparse(node)).body[0])
    node.decorator_list = []
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), env)
    return env[name]


class Point:
    def __init__(self, x, y):
        self._x, self._y = x, y

    def y(self):
        return self._y


class Animation:
    def __init__(self, *args):
        self.target = None
        self.started = False

    def setDuration(self, value):
        pass

    def setStartValue(self, value):
        pass

    def setEndValue(self, value):
        self.target = value

    def setEasingCurve(self, value):
        pass

    def start(self):
        self.started = True


def navigation_action():
    need("QPoint" in imports, "QtCore QPoint is not imported globally")
    bar = NS(minimum=lambda: 0, maximum=lambda: 1000, value=lambda: 0)
    area = NS(widget=lambda: object(), verticalScrollBar=lambda: bar)
    panel = NS(main_tabs=NS(widget=lambda i: area))
    card = NS(mapTo=lambda page, point: Point(0, 400))
    env = dict(
        QPropertyAnimation=Animation,
        QEasingCurve=NS(OutCubic=1),
        QPoint=Point,
        H89_SECTION_SCROLL_MS=100,
        _h89_focus_card=lambda *args: None,
    )
    function("_h89_scroll_to_card", env)(panel, 1, card)
    animation = getattr(panel, "_h89_section_scroll_anim", None)
    need(animation is not None, "section click did not create a scroll animation")
    need(animation.started, "section click scroll animation did not start")
    need(animation.target == 390, f"unexpected section scroll target: {animation.target!r}")


def cursor_fallback_action():
    need("wintypes" in imports, "ctypes.wintypes is not imported globally")

    def cursor(ptr):
        ptr._obj.x, ptr._obj.y = 123, 456
        return 1

    from ctypes import wintypes

    base = dict(
        win32api=None,
        wintypes=wintypes,
        ctypes=NS(byref=ctypes.byref, windll=NS(user32=NS(GetCursorPos=cursor))),
    )
    for name in ("_netease_cursor_pos", "_clock_wake_cursor_pos"):
        result = function(name, dict(base))()
        need(result == (123, 456), f"{name} discarded valid native cursor result: {result!r}")

    # Compatibility contract: several fallback paths intentionally use a module-global
    # wintypes binding. If that binding disappears again, swallowed NameError paths can
    # silently degrade instead of raising a visible exception.
    global_wintypes_users = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(isinstance(n, ast.Name) and n.id == "wintypes" and isinstance(n.ctx, ast.Load) for n in ast.walk(fn)):
            global_wintypes_users.append(fn.name)
    need(global_wintypes_users, "expected global wintypes fallback users are missing")


def liveness_action():
    clock = NS(value=100.0)
    clock.monotonic = lambda: clock.value
    clock.perf_counter = clock.monotonic
    probes = []

    def probe(*args):
        probes.append(1)
        return (False, "corroborated-negative") if len(probes) == 1 else (None, "unavailable")

    env = dict(
        time=clock,
        _h42_windows_frozen=lambda: True,
        _LIMBUS_H42_LIVENESS_PRE=probe,
        H42_FROZEN_NEGATIVE_LIVENESS_BACKOFF_MS=8000,
        _h28_psapi_positive_process_alive=lambda stem: None,
    )
    wrapped = function("_h42_liveness", env)
    stop = threading.Event()

    class Wake:
        def wait(self, seconds):
            clock.value += seconds
            if clock.value >= 100.59:
                stop.set()

        def clear(self):
            pass

    sync = NS(
        _process_stem=lambda s: s,
        _process_hint="kgmusic",
        _lock=threading.Lock(),
        _state={"sync_requested": True},
        _player_liveness_stop_event=stop,
        _player_liveness_wake_event=Wake(),
        _player_liveness_lock=threading.Lock(),
        _player_liveness_stem="kgmusic",
        _player_liveness_confirmed=True,
        _player_liveness_dead_streak=0,
        _player_liveness_serial=1,
        _player_liveness_slow_log_mono=0,
    )
    worker_env = dict(
        time=clock,
        _limbus_bounded_player_liveness_probe=wrapped,
        PLAYER_LIVENESS_DEAD_CONFIRMATIONS=3,
        PLAYER_LIVENESS_POLL_MS=200,
        PLAYER_LIVENESS_SLOW_PROBE_MS=100,
        write_error_log=lambda *args, **kwargs: None,
    )
    worker = function("_h13_player_liveness_worker", worker_env)
    worker(sync)
    need(sync._player_liveness_confirmed is True,
         f"one fresh negative probe became {sync._player_liveness_dead_streak} confirmations")
    need(len(probes) >= 2, "liveness worker did not re-probe after an unconfirmed negative")

    # Genuine shutdown still needs to be detectable from fresh negative evidence.
    stop.clear()
    clock.value = 100.0
    sync._h42_liveness_negative_until = {}
    sync._player_liveness_dead_streak = 0
    env["_LIMBUS_H42_LIVENESS_PRE"] = lambda *args: (False, "fresh-negative")
    worker(sync)
    need(sync._player_liveness_confirmed is False, "three fresh negatives no longer detect exit")

    # Once death is confirmed, frozen-build negative backoff remains available.
    wrapped(sync, "kgmusic")
    need(bool(sync._h42_liveness_negative_until), "confirmed-dead backoff no longer works")

    # Positive process evidence must immediately break the dead backoff.
    env["_h28_psapi_positive_process_alive"] = lambda stem: True
    need(wrapped(sync, "kgmusic")[0] is True, "positive restart evidence cannot break dead backoff")

    # A fresh liveness epoch must not inherit the previous death evidence.
    sync._player_liveness_confirmed = None
    sync._h42_liveness_negative_until = {"kgmusic": 999999.0}
    env["_h28_psapi_positive_process_alive"] = lambda stem: None
    env["_LIMBUS_H42_LIVENESS_PRE"] = lambda *args: (None, "unavailable")
    need(wrapped(sync, "kgmusic")[0] is None, "old negative cache leaked into a fresh liveness epoch")


checks = (navigation_action, cursor_fallback_action, liveness_action)
for check in checks:
    check()
    print(f"PASS {check.__name__}")
print(f"RUNTIME ACTION AUDIT H94F1: PASS ({len(checks)}/{len(checks)})")
