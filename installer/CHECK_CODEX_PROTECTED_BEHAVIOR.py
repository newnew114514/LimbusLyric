from __future__ import annotations
import ast, hashlib, sys
from pathlib import Path

QQ_CLASS_SHA256 = "18f4d65aad1227143579c745161d349ad03530e89aeb6e6487b849ef79f2f0e7"
REQUIRED_FILES = (
    "limbus_netease_native.py",
    "RUN_WITH_EXISTING_BETTERNCM_BRIDGE.cmd",
    "CUSTOM_PLAYER_FOUNDATION.txt",
    "requirements_optional_sync.txt",
    "requirements_word_timing_optional.txt",
    "requirements_audio_emphasis_optional.txt",
    "installer/CHECK_KUGOU_GOLDEN_BASELINE.py",
    "installer/CHECK_KUGOU_CAUSAL_CLOCK_GUARD_REPLAY.py",
    "installer/CHECK_KUGOU_PAUSE_RESUME_CAUSAL_BOOTSTRAP_REPLAY.py",
    "installer/CHECK_KUGOU_POSTSCAN_BASELINE_REPLAY.py",
    "installer/CHECK_LEGACY_BASELINE_INTEGRITY.py",
    "installer/CHECK_RC11_TARGETED_FIXES.py",
    "installer/CHECK_MAIN_SOURCE_LOCK.py",
    "installer/CHECK_DIY_PER_PLAYER_CUSTOM_FONT_REPLAY.py",
)

if len(sys.argv) != 3:
    print("usage: CHECK_CODEX_PROTECTED_BEHAVIOR.py <project-root> <main.py>")
    raise SystemExit(2)

root = Path(sys.argv[1]).resolve()
main = Path(sys.argv[2]).resolve()
source = main.read_text(encoding="utf-8")
tree = ast.parse(source, filename=str(main))
fail = []

qq = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "QQMusicUiAdapter"), None)
if qq is None:
    fail.append("QQMusicUiAdapter missing")
else:
    baseline_path = root / "reference" / "OLD_WORKING_BASELINE_MAIN.py.txt"
    if not baseline_path.is_file():
        fail.append("QQMusicUiAdapter protected baseline source missing")
    else:
        baseline_source = baseline_path.read_text(encoding="utf-8")
        baseline_tree = ast.parse(baseline_source, filename=str(baseline_path))
        baseline_qq = next((n for n in baseline_tree.body if isinstance(n, ast.ClassDef) and n.name == "QQMusicUiAdapter"), None)
        reviewed_r2 = {
            "__init__": "de003ede81f5352701b600bb4ddf493807e3e720824415c983ec810185acefaa",
            "reset_for_track": "0e45eee5dfdab70aa1ef4f4a6a9dfcb9fcde50b18a20afc2dc8454d6617370d4",
            "_make_result": "e27b06ed8eb8e8c214cdae56c0363e79376fa7f6309cd6eed5d358a3aa35ac30",
        }
        if baseline_qq is None:
            fail.append("QQMusicUiAdapter missing from protected baseline source")
        else:
            cur_methods = {n.name:n for n in qq.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
            old_methods = {n.name:n for n in baseline_qq.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
            if set(cur_methods) != set(old_methods):
                fail.append("QQMusicUiAdapter method set changed outside reviewed R2 patch")
            for name, old_node in old_methods.items():
                cur_node = cur_methods.get(name)
                if cur_node is None:
                    continue
                cur_seg = ast.get_source_segment(source, cur_node)
                actual = hashlib.sha256(cur_seg.encode("utf-8")).hexdigest()
                if name in reviewed_r2:
                    if actual != reviewed_r2[name]:
                        fail.append("QQMusicUiAdapter reviewed R2 method changed: " + name)
                else:
                    old_seg = ast.get_source_segment(baseline_source, old_node)
                    expected = hashlib.sha256(old_seg.encode("utf-8")).hexdigest()
                    if actual != expected:
                        fail.append("QQMusicUiAdapter protected method changed: " + name)
            if "R2 QQ播放器时长推进自证" not in source or "duration_self_proved" not in source:
                fail.append("QQMusicUiAdapter reviewed R2 duration-proof contract missing")

for rel in REQUIRED_FILES:
    if not (root / rel).exists():
        fail.append("protected/support file missing: " + rel)

if "LIMBUSLYRIC_NETEASE_INTERNAL_BRIDGE', '0'" not in source:
    fail.append("BetterNCM Bridge default is no longer opt-in/off")
if "netease-cloudmusic-detector==2.0.6" not in (root / "requirements_netease_native.txt").read_text(encoding="utf-8"):
    fail.append("NetEase native detector pin missing")
if "pywin32==311" not in (root / "requirements_core.txt").read_text(encoding="utf-8"):
    fail.append("pywin32==311 packaging compatibility pin missing")

opener = (root / "OPEN_LOG_FOLDER.cmd").read_text(encoding="utf-8", errors="ignore")
if r"%LOCALAPPDATA%\LimbusLyric\logs" not in opener:
    fail.append("unified LOCALAPPDATA log opener behavior changed")

if fail:
    print("CODEX PROTECTED BEHAVIOR: FAIL")
    for item in fail:
        print("  - " + item)
    raise SystemExit(33)

print("CODEX PROTECTED BEHAVIOR: PASS")
print("  QQMusicUiAdapter old-working methods + reviewed R2 duration-proof lock: PASS")
print("  protected/support files present: " + str(len(REQUIRED_FILES)))
print("  NetEase Native / BetterNCM opt-in invariant: PASS")
print("  pywin32==311 / unified LOCALAPPDATA logs invariant: PASS")
