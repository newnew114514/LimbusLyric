#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: RUN_RELEASE_RESUME_VALIDATION.py <project-root> <main.py>")
root = Path(sys.argv[1]).resolve()
main = Path(sys.argv[2]).resolve()
env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"
checks = (
    "CHECK_NETEASE_TEMPORAL_RAIL_CACHED_WITNESS_H29_REPLAY.py",
    "CHECK_FROZEN_KUGOU_CAPABILITY_SAFETY_H42_REPLAY.py",
    "CHECK_KUGOU_CLOCK_DEADLOCK_STARTUP_MOTION_H43_REPLAY.py",
)
for name in checks:
    proc = subprocess.run([sys.executable, str(root / "installer" / name), str(main)], env=env, text=True)
    if proc.returncode:
        print(f"RELEASE RESUME VALIDATION: FAIL ({name}, exit={proc.returncode})")
        raise SystemExit(proc.returncode)
print("RELEASE RESUME VALIDATION: PASS")
print("  H29/H42/H43 replay set verified through one aggregate resume entrypoint.")
