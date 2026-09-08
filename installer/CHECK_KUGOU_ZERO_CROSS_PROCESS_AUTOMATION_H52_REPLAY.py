from pathlib import Path
import ast
import os
import sys
import time
import types


if len(sys.argv) < 2:
    raise SystemExit(2)

source = Path(sys.argv[1]).read_text(encoding="utf-8")
logs = [Path(path).read_text(encoding="utf-8", errors="replace") for path in sys.argv[2:]] or ["""
[2026-09-03 16:43:39] 运行环境 | windows=10.0.26200 | python=3.12.6 | frozen=1
[2026-09-03 16:43:43] H48酷狗跨进程UIA唤醒已跳过 | process=kgmusic.exe
[2026-09-03 16:44:45] 收到退出请求 | state=RUNNING->STOPPING
[2026-09-03 16:44:47] 酷狗宿主V2进度候选证明中 | position=1170ms
[2026-09-03 16:44:50] 停止组件等待超时 | component=native-workers | elapsed=5205.4ms
[2026-09-03 16:44:51] 进程退出兜底触发 | action=os._exit
"""]


def need(condition, message):
    if not condition:
        print("KUGOU ZERO CROSS-PROCESS AUTOMATION H52 REPLAY: FAIL")
        print(" - " + message)
        raise SystemExit(1)


affected = [
    log for log in logs
    if "windows=10.0.26200" in log
    and "frozen=1" in log
    and "H48酷狗跨进程UIA唤醒已跳过" in log
]
need(affected, "logs do not include the affected packaged Windows 26200 H48 session")

stuck = False
for log in affected:
    stop = log.find("收到退出请求")
    late_host = log.find("酷狗宿主V2进度候选证明中", stop + 1)
    timeout = log.find("component=native-workers", late_host + 1)
    hard_exit = log.find("action=os._exit", timeout + 1)
    if min(stop, late_host, timeout, hard_exit) >= 0:
        stuck = True
        break
need(stuck, "logs do not reproduce a KuGou HostV2 worker surviving shutdown and forcing os._exit")

tree = ast.parse(source)
functions = {
    node.name: node for node in tree.body
    if isinstance(node, ast.FunctionDef)
}


class FakeSys:
    platform = "win32"
    frozen = True
    build = 26200

    @classmethod
    def getwindowsversion(cls):
        return types.SimpleNamespace(build=cls.build)


# Prove the old policy misses this user's exact build before exercising H52.
baseline_nodes = [functions[name] for name in (
    "_h22_windows_build_number",
    "_h22_kugou_win10_frozen_safe_mode",
    "_h23_windows_build_number",
    "_h23_kugou_win10_frozen_no_accessibility",
)]
baseline = {"sys": FakeSys, "os": os, "H22_KUGOU_WIN10_FROZEN_SAFE_MODE": True,
            "H22_KUGOU_WIN10_HOST_UIA_OPTIN": False}
exec(compile(ast.Module(body=baseline_nodes, type_ignores=[]), "<h52-baseline>", "exec"), baseline)
need(not baseline["_h22_kugou_win10_frozen_safe_mode"](),
     "field fixture no longer reproduces H22's build-26200 policy hole")
need(not baseline["_h23_kugou_win10_frozen_no_accessibility"](),
     "field fixture no longer reproduces H23's build-26200 policy hole")

need("+ KUGOU ZERO CROSS-PROCESS ACCESSIBILITY H52" in source,
     "missing H52 packaged-KuGou zero-accessibility policy")
need("_h52_kugou_no_cross_process_accessibility" in functions and "_h52_activate_runtime" in functions,
     "H52 runtime policy is not independently replayable")


def legacy_policy():
    return bool(FakeSys.platform.startswith("win") and FakeSys.frozen and 0 < FakeSys.build < 22000)


class PlayerUiPositionReader:
    @staticmethod
    def _kugou_win10_frozen_no_uia():
        return legacy_policy()


runtime = {
    "sys": FakeSys,
    "os": os,
    "PlayerUiPositionReader": PlayerUiPositionReader,
    "_h22_kugou_win10_frozen_safe_mode": legacy_policy,
    "_h23_kugou_win10_frozen_no_accessibility": legacy_policy,
}
exec(compile(ast.Module(body=[
    functions["_h52_kugou_no_cross_process_accessibility"],
    functions["_h52_activate_runtime"],
], type_ignores=[]), "<h52-runtime>", "exec"), runtime)
runtime["_h52_activate_runtime"]()

need(runtime["_h22_kugou_win10_frozen_safe_mode"](), "HostV2/point/hidden/wake gates still admit build 26200")
need(runtime["_h23_kugou_win10_frozen_no_accessibility"](), "MSAA/duration-hint gates still admit build 26200")
need(PlayerUiPositionReader._kugou_win10_frozen_no_uia(), "worker can still initialize UIA on build 26200")

# Preserve known compatibility scopes: old Win10 remains protected; ordinary Win11,
# source mode and non-Windows builds keep their existing capability lanes.
FakeSys.build = 19045
need(runtime["_h22_kugou_win10_frozen_safe_mode"](), "legacy Win10 H22 protection regressed")
need(runtime["_h23_kugou_win10_frozen_no_accessibility"](), "legacy Win10 H23 protection regressed")
need(PlayerUiPositionReader._kugou_win10_frozen_no_uia(), "legacy Win10 no-UIA-init protection regressed")
FakeSys.build = 26100
need(not runtime["_h52_kugou_no_cross_process_accessibility"](), "unaffected Win11 build was broadened")
FakeSys.build = 26200
FakeSys.frozen = False
need(not runtime["_h52_kugou_no_cross_process_accessibility"](), "source/debug mode was broadened")
FakeSys.frozen = True
FakeSys.platform = "linux"
need(not runtime["_h52_kugou_no_cross_process_accessibility"](), "non-Windows mode was broadened")
FakeSys.platform = "win32"

print("KUGOU ZERO CROSS-PROCESS AUTOMATION H52 REPLAY: PASS")
print(" - affected H48 field session reproduces the post-exit HostV2 native-worker hang")
print(" - build 26200 reuses every existing KuGou accessibility fail-closed gate")
print(" - build 26100, source mode and non-Windows behavior remain unchanged")
