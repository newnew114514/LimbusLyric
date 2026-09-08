from __future__ import annotations

from pathlib import Path

# Canonical source-payload boundary shared by release audits and packaging checks.
# Build/runtime artifacts may exist inside the project tree during a Windows build,
# but they are never part of the source payload or SHA256_FILES.txt.
EXCLUDED_TOP = frozenset({
    ".git",
    ".build_installer_venv_ascii",
    ".build_venv",
    ".pyinstaller_work",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "installer_output",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
    "logs",
})

EXCLUDED_PREFIXES = (
    ("installer", "release"),
    ("installer", "offline_cache"),
)

EXCLUDED_FILES = frozenset({
    ("installer", "PACKAGING_SMOKE_RESULT.txt"),
})


def source_payload_path(root: Path, path: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    parts = rel.parts
    if not parts:
        return True
    if parts[0] in EXCLUDED_TOP:
        return False
    # Python bytecode caches are ephemeral runtime/build artifacts no matter where
    # they appear. They must never enter SHA256_FILES.txt or the canonical source ZIP.
    if "__pycache__" in parts or (path.is_file() and path.suffix.lower() in {".pyc", ".pyo"}):
        return False
    for prefix in EXCLUDED_PREFIXES:
        if len(parts) >= len(prefix) and parts[:len(prefix)] == prefix:
            return False
    if parts in EXCLUDED_FILES:
        return False
    return True
