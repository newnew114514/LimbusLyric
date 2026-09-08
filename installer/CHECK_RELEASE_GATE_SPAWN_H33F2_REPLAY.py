from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_RELEASE_GATE_SPAWN_H33F2_REPLAY.py <project-root>")
root = Path(sys.argv[1]).resolve()
runner_path = root / "installer" / "RUN_RELEASE_GATE_SUITE.py"
source = runner_path.read_text(encoding="utf-8")

# Source contract: do not regress to spawning every gate through the venv launcher
# under the SUBST project drive, and keep Windows concurrency conservative.
assert 'getattr(sys, "_base_executable", None)' in source
assert 'WINDOWS_DEFAULT_MAX_WORKERS = 2' in source
assert 'SPAWN_RETRY_DELAYS' in source
assert 'except FileNotFoundError as exc:' in source
assert 'all paths still exist' in source
assert 'subprocess.Popen([sys.executable' not in source

spec = importlib.util.spec_from_file_location("limbus_gate_runner_h33f2", runner_path)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
selected = mod._select_gate_python()
assert selected.is_file(), selected

# Functional replay: use the runner itself on many tiny stdlib-only gates.  This
# verifies that interpreter selection is independent of project/runtime imports.
with tempfile.TemporaryDirectory(prefix="limbus-h33f2-spawn-") as td:
    fixture = Path(td)
    inst = fixture / "installer"
    inst.mkdir(parents=True)
    main = fixture / mod.MAIN_NAME
    main.write_text("print('fixture-main')\n", encoding="utf-8")
    rows = []
    for i in range(12):
        name = f"CHECK_SPAWN_FIX_{i:02d}.py"
        (inst / name).write_text(f"print('spawn-fixture-{i:02d}')\n", encoding="utf-8")
        rows.append(f"{name}\troot\n")
    (inst / mod.GATE_SUITE_NAME).write_text("".join(rows), encoding="utf-8")
    env = os.environ.copy()
    env["LIMBUSLYRIC_GATE_WORKERS"] = "4"
    proc = subprocess.run(
        [str(selected), str(runner_path), str(fixture), str(main)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=60,
        env=env,
    )
    out = proc.stdout or ""
    assert proc.returncode == 0, out
    assert "PASS (12/12)" in out, out
    assert "gate-python=" in out, out

print("RELEASE GATE SPAWN H33F2 REPLAY: PASS")
print(" - release gates use the stable base interpreter instead of the SUBST build-venv launcher")
print(" - Windows default concurrency is bounded to 2 unless explicitly overridden")
print(" - transient FileNotFoundError spawn failures are retried with path diagnostics")
