from __future__ import annotations

import sys
from pathlib import Path

from SOURCE_MANIFEST import sync_safe_additions

if len(sys.argv) != 2:
    raise SystemExit("usage: SYNC_SOURCE_MANIFEST_ADDITIONS.py <root>")
root = Path(sys.argv[1]).resolve()
try:
    added, unsafe = sync_safe_additions(root)
except Exception as exc:
    print(f"SOURCE MANIFEST SAFE-SYNC: FAIL ({exc})")
    raise SystemExit(42)
if unsafe:
    print("SOURCE MANIFEST SAFE-SYNC: FAIL")
    print("  New source payload is not auto-enrolled because it is not a registered CHECK_* gate or NOTE/AUDIT document:")
    for rel in unsafe[:20]:
        print(f"  - {rel}")
    print("  If these files are intentional, run installer\\PREPARE_SOURCE_MANIFEST.py once from the reviewed source tree.")
    raise SystemExit(43)
if added:
    print(f"SOURCE MANIFEST SAFE-SYNC: PASS (auto-added={len(added)})")
    for rel in added:
        print(f"  + {rel}")
else:
    print("SOURCE MANIFEST SAFE-SYNC: PASS (no additions)")
