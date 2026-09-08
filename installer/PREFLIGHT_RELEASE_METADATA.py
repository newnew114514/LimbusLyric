from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

if len(sys.argv) != 3:
    raise SystemExit("usage: PREFLIGHT_RELEASE_METADATA.py <root> <main.py>")
root = Path(sys.argv[1]).resolve()
main = Path(sys.argv[2]).resolve()
env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"


def run(label: str, cmd: list[str]) -> int:
    proc = subprocess.run(cmd, text=True, capture_output=True, env=env)
    text = (proc.stdout or "") + (proc.stderr or "")
    if text.strip():
        print(text.rstrip())
    if proc.returncode:
        print(f"  preflight step failed: {label} (exit={proc.returncode})")
    return proc.returncode

# Trust anchor first: a metadata repair must never run against an unlocked main.
if run("main-source-lock", [sys.executable, str(root / "installer" / "CHECK_MAIN_SOURCE_LOCK.py"), str(main)]):
    print("RELEASE METADATA PREFLIGHT: FAIL")
    raise SystemExit(41)

# Gate registration is semantic metadata. Validate it before allowing the safe
# manifest sync to refresh RELEASE_GATE_SUITE.tsv's derived SHA entry.
if run("release-gate-coverage", [sys.executable, str(root / "installer" / "CHECK_RELEASE_GATE_COVERAGE.py"), str(root)]):
    print("RELEASE METADATA PREFLIGHT: FAIL")
    raise SystemExit(42)

# A normal Hxx patch adds a registered CHECK_* replay and/or NOTE/AUDIT document.
# Add those files automatically; existing source hashes remain immutable except
# RELEASE_GATE_SUITE.tsv after the exact gate-coverage check above.
if run("source-manifest-safe-sync", [sys.executable, str(root / "installer" / "SYNC_SOURCE_MANIFEST_ADDITIONS.py"), str(root)]):
    print("RELEASE METADATA PREFLIGHT: FAIL")
    raise SystemExit(43)

failed: list[tuple[str, int]] = []
checks = [
    ("source-payload-structure", [sys.executable, str(root / "installer" / "CHECK_PACKAGING_STRUCTURE.py"), str(root)]),
]
for label, cmd in checks:
    code = run(label, cmd)
    if code:
        failed.append((label, code))
if failed:
    print("RELEASE METADATA PREFLIGHT: FAIL")
    for label, code in failed:
        print(f"  - {label}: exit={code}")
    raise SystemExit(44)
print("RELEASE METADATA PREFLIGHT: PASS")
