from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PACKAGING_PATH_POLICY import EXCLUDED_TOP, EXCLUDED_PREFIXES


def is_project_source_path(root: Path, path: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    parts = rel.parts
    if not parts or parts[0] in EXCLUDED_TOP:
        return False
    for prefix in EXCLUDED_PREFIXES:
        if len(parts) >= len(prefix) and parts[:len(prefix)] == prefix:
            return False
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: CLEAN_PROJECT_PYTHON_CACHE.py <project-root>")
        return 2

    root = Path(sys.argv[1]).resolve()
    removed_dirs = 0
    removed_files = 0

    # Remove cache directories first. Restrict cleanup to the same project-source
    # area audited by CHECK_RELEASE_INVARIANTS.py; never touch the build venv,
    # PyInstaller work tree, dist/build outputs, or installer/release artifacts.
    cache_dirs = sorted(
        (
            p
            for p in root.rglob("__pycache__")
            if p.is_dir() and is_project_source_path(root, p)
        ),
        key=lambda p: len(p.parts),
        reverse=True,
    )
    for cache_dir in cache_dirs:
        shutil.rmtree(cache_dir, ignore_errors=True)
        if not cache_dir.exists():
            removed_dirs += 1

    # Also remove loose .pyc files that are not inside a conventional cache dir.
    for pyc in list(root.rglob("*.pyc")):
        if not pyc.is_file() or not is_project_source_path(root, pyc):
            continue
        try:
            pyc.unlink()
            removed_files += 1
        except FileNotFoundError:
            pass

    leftovers = [
        p
        for p in root.rglob("*")
        if is_project_source_path(root, p)
        and ((p.is_dir() and p.name == "__pycache__") or (p.is_file() and p.suffix.lower() == ".pyc"))
    ]
    if leftovers:
        print("PROJECT PYTHON CACHE CLEAN: FAIL")
        for item in leftovers[:10]:
            print("  " + str(item.relative_to(root)))
        return 21

    print(
        "PROJECT PYTHON CACHE CLEAN: PASS "
        f"(removed_dirs={removed_dirs} removed_loose_pyc={removed_files})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
