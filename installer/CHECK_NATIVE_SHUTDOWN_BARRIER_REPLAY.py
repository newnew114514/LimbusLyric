from pathlib import Path
import sys


if len(sys.argv) != 2:
    raise SystemExit(2)
text = Path(sys.argv[1]).read_text(encoding="utf-8")


def need(condition, message):
    if not condition:
        print("NATIVE SHUTDOWN BARRIER REPLAY: FAIL")
        print(" - " + message)
        raise SystemExit(1)


need("UnhookWindowsHookEx" in text, "WH_MOUSE_LL hook is never unhooked")
need("+ NATIVE SHUTDOWN BARRIER H47" in text, "H47 build marker is missing")
need("PostThreadMessageW" in text and "WM_QUIT" in text, "hook GetMessage loop has no stop signal")
need("thread.join(" in text, "native workers are not joined before interpreter teardown")
need("native-clean=1" in text, "shutdown does not prove native workers stopped")

exit_start = text.index("def _limbus_control_panel_exit_app_bounded")
exit_end = text.index("ControlPanel._exit_app =", exit_start)
need("QApplication.quit()" not in text[exit_start:exit_end],
     "Qt still exits before asynchronous provider cleanup finishes")

print("NATIVE SHUTDOWN BARRIER REPLAY: PASS")
print(" - hook uninstalls and wakes its GetMessage thread")
print(" - native workers finish before Qt permits interpreter teardown")
print(" - existing hard watchdog remains the bounded fallback")
