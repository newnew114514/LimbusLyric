from __future__ import annotations

import sys
from pathlib import Path

from SOURCE_MANIFEST import read_gate_suite

if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_RELEASE_GATE_COVERAGE.py <root>")
root = Path(sys.argv[1]).resolve()
installer = root / "installer"
try:
    declared = read_gate_suite(root)
except Exception as exc:
    print(f"RELEASE GATE COVERAGE: FAIL ({exc})")
    raise SystemExit(46)
actual = {p.name for p in installer.glob("CHECK_*.py") if p.is_file()}
missing = sorted(actual - set(declared), key=str.casefold)
extra = sorted(set(declared) - actual, key=str.casefold)
invalid_modes = sorted(name for name, mode in declared.items() if mode not in {"main", "root", "root-main"})
if missing or extra or invalid_modes:
    print("RELEASE GATE COVERAGE: FAIL")
    if missing:
        print("  CHECK_* files not registered in RELEASE_GATE_SUITE.tsv:")
        for name in missing[:30]: print(f"  - {name}")
    if extra:
        print("  RELEASE_GATE_SUITE.tsv entries without files:")
        for name in extra[:30]: print(f"  - {name}")
    if invalid_modes:
        print("  Invalid gate arg-mode entries:")
        for name in invalid_modes[:30]: print(f"  - {name}: {declared[name]}")
    raise SystemExit(47)
print(f"RELEASE GATE COVERAGE: PASS (registered={len(declared)} check_files={len(actual)})")
