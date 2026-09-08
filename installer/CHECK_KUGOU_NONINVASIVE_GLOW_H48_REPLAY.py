from pathlib import Path
import ast
import sys
import types


if len(sys.argv) not in (2, 3):
    raise SystemExit(2)

source = Path(sys.argv[1])
text = source.read_text(encoding="utf-8")


def need(condition, message):
    if not condition:
        print("KUGOU NONINVASIVE + GLOW H48 REPLAY: FAIL")
        print(" - " + message)
        raise SystemExit(1)


if len(sys.argv) == 3:
    field = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")
    need("windows=10.0.26200" in field and "frozen=1" in field,
         "field fixture is not the affected packaged Windows 26200 environment")
    need("UIA无障碍唤醒完成 | process=kgmusic.exe | hwnds=2 | touched=4" in field,
         "field fixture does not reproduce invasive KuGou accessibility wake")
    need("atlas_inflight=1" in field and "glow/vector=skip" in field,
         "field fixture does not reproduce configured glow being skipped during atlas warmup")

for marker in (
    "+ KUGOU NONINVASIVE ACCESSIBILITY + WARMUP GLOW H48",
    "H48酷狗跨进程UIA唤醒已跳过",
    "windows-frozen-kugou-no-accessibility-wake",
):
    need(marker in text, "missing H48 marker: " + marker)

tree = ast.parse(text)
wanted = {
    "_limbus_render_emergency_active",
    "_h48_should_skip_kugou_accessibility",
    "_h48_activate_runtime",
}
nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
need({node.name for node in nodes} == wanted, "H48 behavior is not independently replayable")

logs = []


def write_error_log(*args, **kwargs):
    logs.append((args, kwargs))


class AsyncPlayerUiPositionReader:
    def _kick_accessibility(self, process_name):
        self.base_calls = getattr(self, "base_calls", 0) + 1
        return "base"


class Atlas:
    def isNull(self):
        return False


class Window:
    def __init__(self):
        self._song_fragment_atlas_fuse_reason = ""
        self._song_fragment_atlas_inflight = {"style|song"}
        self._limbus_render_emergency_fused = False
        self._limbus_render_emergency_reason = ""
        self._song_fragment_atlas_pixmap = None
        self._song_fragment_atlas_performance_fused = False


fake_sys = types.SimpleNamespace(platform="win32", frozen=True)
runtime = {
    "sys": fake_sys,
    "os": __import__("os"),
    "AsyncPlayerUiPositionReader": AsyncPlayerUiPositionReader,
    "write_error_log": write_error_log,
    "_limbus_restore_visual_timer_cadence": lambda window: None,
}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), runtime)

need(runtime["_limbus_render_emergency_active"](Window()) is False,
     "ordinary atlas warmup still removes glow through the emergency plain-glyph renderer")
w = Window()
w._limbus_render_emergency_fused = True
w._limbus_render_emergency_reason = "paint-hard-budget"
need(runtime["_limbus_render_emergency_active"](w) is True,
     "real hard-paint overload no longer fails closed")

runtime["_h48_activate_runtime"]()
reader = AsyncPlayerUiPositionReader()
need(reader._kick_accessibility("kgmusic.exe") is None and getattr(reader, "base_calls", 0) == 0,
     "packaged Windows KuGou still enters cross-process accessibility wake")
need(reader._kick_accessibility("qqmusic.exe") == "base" and reader.base_calls == 1,
     "the KuGou-only guard changed QQ behavior")
fake_sys.frozen = False
need(reader._kick_accessibility("kgmusic.exe") == "base" and reader.base_calls == 2,
     "source/dev KuGou behavior was changed")

print("KUGOU NONINVASIVE + GLOW H48 REPLAY: PASS")
print(" - packaged Windows KuGou never enters the invasive accessibility wake")
print(" - ordinary atlas warmup retains glow; only measured hard-paint overload degrades")
print(" - QQ and non-frozen development behavior remain unchanged")
