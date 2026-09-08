from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_RELEASE_GATE_SUITE_REPLAY.py <project-root>")
project = Path(sys.argv[1]).resolve()
runner = project / "installer" / "RUN_RELEASE_GATE_SUITE.py"

with tempfile.TemporaryDirectory(prefix="limbus-gate-suite-") as td:
    root = Path(td)
    installer = root / "installer"
    installer.mkdir(parents=True)
    main = root / "LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"
    main.write_text("print('fixture')\n", encoding="utf-8")
    (installer / "CHECK_FIX_FAIL_A.py").write_text("print('fixture A failed')\nraise SystemExit(21)\n", encoding="utf-8")
    (installer / "CHECK_FIX_PASS.py").write_text("print('fixture pass')\n", encoding="utf-8")
    (installer / "CHECK_FIX_FAIL_B.py").write_text("print('fixture B failed')\nraise SystemExit(22)\n", encoding="utf-8")
    (installer / "RELEASE_GATE_SUITE.tsv").write_text(
        "CHECK_FIX_FAIL_A.py\tmain\n"
        "CHECK_FIX_PASS.py\troot\n"
        "CHECK_FIX_FAIL_B.py\tmain\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(runner), str(root), str(main)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=30,
    )
    out = proc.stdout or ""
    assert proc.returncode != 0, out
    assert "CHECK_FIX_FAIL_A.py" in out and "fixture A failed" in out, out
    assert "CHECK_FIX_FAIL_B.py" in out and "fixture B failed" in out, out
    assert "PASS CHECK_FIX_PASS.py" in out and "fixture pass" not in out, out
    assert "FAIL (2/3)" in out and "no first-failure masking" in out, out

print("RELEASE GATE SUITE REPLAY: PASS")
print("  declarative suite continues after failures and reports every failing gate")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# A failed aggregate run must retain successful per-gate results. If only the
# failing CHECK_*.py expectation is corrected, unchanged PASS gates are reused;
# shared source changes still invalidate the cache via the common manifest digest.
with tempfile.TemporaryDirectory(prefix="limbus-gate-partial-cache-") as td:
    root = Path(td)
    installer = root / "installer"
    installer.mkdir(parents=True)
    main = root / "LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"
    main.write_text("print('cache fixture')\n", encoding="utf-8")
    fail_gate = installer / "CHECK_CACHE_FAIL.py"
    pass_gate = installer / "CHECK_CACHE_PASS.py"
    fail_gate.write_text("print('cache fail')\nraise SystemExit(31)\n", encoding="utf-8")
    pass_gate.write_text("print('cache pass executed')\n", encoding="utf-8")
    (installer / "RELEASE_GATE_SUITE.tsv").write_text(
        "CHECK_CACHE_FAIL.py\tmain\n"
        "CHECK_CACHE_PASS.py\tmain\n",
        encoding="utf-8",
    )

    def write_manifest():
        rows = []
        for path in (main, fail_gate, pass_gate):
            rows.append(f"{_sha256(path)}  {path.relative_to(root).as_posix()}")
        (root / "SHA256_FILES.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")

    write_manifest()
    first = subprocess.run(
        [sys.executable, str(runner), str(root), str(main)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=30,
    )
    first_out = first.stdout or ""
    assert first.returncode != 0, first_out
    assert "PASS CHECK_CACHE_PASS.py" in first_out and "(cached)" not in first_out, first_out

    # Correct only the failed gate itself. Because CHECK_*.py rows are deliberately
    # excluded from the shared-input fingerprint, the earlier unrelated PASS survives.
    fail_gate.write_text("print('cache fixed')\n", encoding="utf-8")
    write_manifest()
    second = subprocess.run(
        [sys.executable, str(runner), str(root), str(main)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=30,
    )
    second_out = second.stdout or ""
    assert second.returncode == 0, second_out
    assert "PASS CHECK_CACHE_PASS.py (cached)" in second_out, second_out
    assert "PASS CHECK_CACHE_FAIL.py (cached)" not in second_out, second_out

print("RELEASE GATE PARTIAL CACHE REPLAY: PASS")
print("  successful gates survive a gate-only expectation fix; shared payload changes invalidate them")

