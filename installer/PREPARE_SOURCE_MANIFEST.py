from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from SOURCE_MANIFEST import regenerate_manifest

if len(sys.argv) != 2:
    raise SystemExit("usage: PREPARE_SOURCE_MANIFEST.py <root>")
root = Path(sys.argv[1]).resolve()
main = root / "LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"
env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"

# Full refresh is a maintainer action. Never bless an unreviewed main source.
lock = subprocess.run(
    [sys.executable, str(root / "installer" / "CHECK_MAIN_SOURCE_LOCK.py"), str(main)],
    text=True,
    env=env,
)
if lock.returncode:
    print("SOURCE MANIFEST PREPARE: FAIL (main source lock must pass before a full refresh)")
    raise SystemExit(44)
coverage = subprocess.run(
    [sys.executable, str(root / "installer" / "CHECK_RELEASE_GATE_COVERAGE.py"), str(root)],
    text=True,
    env=env,
)
if coverage.returncode:
    print("SOURCE MANIFEST PREPARE: FAIL (release gate coverage must pass before a full refresh)")
    raise SystemExit(45)
entries = regenerate_manifest(root)
print(f"SOURCE MANIFEST PREPARE: PASS (files={len(entries)})")
print("  SHA256_FILES.txt regenerated deterministically from the canonical source payload.")
