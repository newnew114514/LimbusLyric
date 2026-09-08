from __future__ import annotations

import sys
import zipfile
from pathlib import Path, PurePosixPath

from PACKAGING_PATH_POLICY import source_payload_path, EXCLUDED_TOP, EXCLUDED_PREFIXES
from SOURCE_MANIFEST import payload_files, read_manifest, sha256_file

if len(sys.argv) not in (2, 3):
    raise SystemExit("usage: CHECK_PACKAGING_STRUCTURE.py <root> [release.zip]")

root = Path(sys.argv[1]).resolve()
main_name = "LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"


def included(path: Path) -> bool:
    return source_payload_path(root, path)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


main_files = [path for path in root.rglob(main_name) if included(path)]
need(main_files == [root / main_name], f"expected one root main source, got {main_files}")

installer_roots = [
    path for path in root.rglob("installer")
    if path.is_dir() and included(path) and (path / "BUILD_RELEASE.cmd").is_file()
]
need(installer_roots == [root / "installer"], f"expected one root installer, got {installer_roots}")

canonical_roots = []
for candidate in [root, *[path for path in root.rglob("*") if path.is_dir() and included(path)]]:
    if (candidate / main_name).is_file() and (candidate / "installer" / "BUILD_RELEASE.cmd").is_file():
        canonical_roots.append(candidate)
need(canonical_roots == [root], f"nested/duplicate canonical roots: {canonical_roots}")

def source_cache_artifact(path: Path) -> bool:
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
    return bool("__pycache__" in parts or (path.is_file() and path.suffix.lower() in {".pyc", ".pyo"}))

caches = [path for path in root.rglob("*") if source_cache_artifact(path)]
need(not caches, f"python cache artifacts present: {caches[:10]}")

manifest = read_manifest(root)
payload = payload_files(root)
need(set(manifest) == set(payload), (
    f"manifest coverage mismatch missing={sorted(set(payload) - set(manifest))[:10]} "
    f"extra={sorted(set(manifest) - set(payload))[:10]}"
))
for rel, path in payload.items():
    actual = sha256_file(path)
    need(manifest[rel] == actual, f"manifest hash mismatch: {rel}")

if len(sys.argv) == 3:
    archive = Path(sys.argv[2]).resolve()
    with zipfile.ZipFile(archive) as zf:
        files = [PurePosixPath(name) for name in zf.namelist() if name and not name.endswith("/")]
        need(files, "release ZIP is empty")
        prefixes = {path.parts[0] for path in files if path.parts}
        need(len(prefixes) == 1, f"release ZIP must have one top-level root, got {sorted(prefixes)}")
        prefix = next(iter(prefixes))
        rel_files = {PurePosixPath(*path.parts[1:]).as_posix() for path in files}
        need(main_name in rel_files, "release ZIP root main source missing")
        need("installer/BUILD_RELEASE.cmd" in rel_files, "release ZIP root installer missing")
        need(sum(1 for rel in rel_files if rel == main_name) == 1, "duplicate main source in ZIP")
        need(not any("__pycache__" in PurePosixPath(rel).parts or rel.lower().endswith(".pyc") for rel in rel_files),
             "python cache artifact in ZIP")
        need(set(payload) | {"SHA256_FILES.txt"} == rel_files,
             f"ZIP payload differs from canonical root {prefix}")

print("PACKAGING STRUCTURE: PASS")
print(f"  canonical roots=1 main sources=1 installer roots=1 manifest_files={len(manifest)}")
if len(sys.argv) == 3:
    print("  release ZIP top-level roots=1 payload=canonical source root")
