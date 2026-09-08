from __future__ import annotations

import hashlib
import re
from pathlib import Path

from PACKAGING_PATH_POLICY import source_payload_path

MANIFEST_NAME = "SHA256_FILES.txt"
_GATE_LINE_RE = re.compile(r"^([^#\t][^\t]*)\t(main|root|root-main)$")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_files(root: Path) -> dict[str, Path]:
    root = Path(root).resolve()
    manifest_path = root / MANIFEST_NAME
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and source_payload_path(root, path) and path != manifest_path
    }


def read_manifest(root: Path) -> dict[str, str]:
    path = Path(root).resolve() / MANIFEST_NAME
    if not path.is_file():
        raise FileNotFoundError(f"source manifest missing: {path}")
    result: dict[str, str] = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            digest, rel = raw.split(None, 1)
        except ValueError as exc:
            raise ValueError(f"invalid source manifest line {lineno}: {raw!r}") from exc
        rel = rel.strip().replace("\\", "/")
        digest = digest.strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"invalid sha256 at line {lineno}: {digest!r}")
        if rel in result:
            raise ValueError(f"duplicate manifest path at line {lineno}: {rel}")
        result[rel] = digest
    return result


def write_manifest(root: Path, entries: dict[str, str]) -> None:
    path = Path(root).resolve() / MANIFEST_NAME
    text = "".join(f"{entries[rel]}  {rel}\n" for rel in sorted(entries, key=str.casefold))
    path.write_text(text, encoding="utf-8", newline="\n")


def regenerate_manifest(root: Path) -> dict[str, str]:
    files = payload_files(root)
    entries = {rel: sha256_file(path) for rel, path in files.items()}
    write_manifest(root, entries)
    return entries


def read_gate_suite(root: Path) -> dict[str, str]:
    suite_path = Path(root).resolve() / "installer" / "RELEASE_GATE_SUITE.tsv"
    result: dict[str, str] = {}
    if not suite_path.is_file():
        return result
    for lineno, raw in enumerate(suite_path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _GATE_LINE_RE.fullmatch(stripped)
        if not match:
            raise ValueError(f"invalid release gate suite line {lineno}: {raw!r}")
        name, mode = match.groups()
        if name in result:
            raise ValueError(f"duplicate release gate suite entry: {name}")
        result[name] = mode
    return result


def safe_auto_addition(root: Path, rel: str, suite: dict[str, str] | None = None) -> bool:
    """Allow only additive release metadata that is expected to accompany a new Hxx patch.

    Existing hashes are never silently refreshed. Unknown new payload remains fatal.
    """
    p = Path(rel)
    parts = p.parts
    if len(parts) == 1 and p.suffix.lower() in {".md", ".txt"}:
        name = p.name.upper()
        if "_NOTE_" in name or "_AUDIT_" in name:
            return True
    if len(parts) == 2 and parts[0].lower() == "installer" and p.suffix.lower() == ".py":
        name = p.name
        suite = suite if suite is not None else read_gate_suite(root)
        if name.startswith("CHECK_") and name in suite:
            return True
    return False


def sync_safe_additions(root: Path) -> tuple[list[str], list[str]]:
    root = Path(root).resolve()
    manifest = read_manifest(root)
    files = payload_files(root)
    missing = sorted(set(files) - set(manifest), key=str.casefold)
    suite = read_gate_suite(root)
    safe = [rel for rel in missing if safe_auto_addition(root, rel, suite)]
    unsafe = [rel for rel in missing if rel not in safe]
    if unsafe:
        return safe, unsafe

    # RELEASE_GATE_SUITE.tsv is registration metadata. It is the one existing
    # manifest entry allowed to refresh automatically, and only when its current
    # declarations exactly cover every CHECK_*.py file. This lets a normal Hxx
    # patch register a new replay without requiring a second manual SHA edit.
    suite_rel = "installer/RELEASE_GATE_SUITE.tsv"
    actual_checks = {p.name for p in (root / "installer").glob("CHECK_*.py") if p.is_file()}
    suite_coherent = set(suite) == actual_checks

    updated = dict(manifest)
    changed = False
    for rel in safe:
        updated[rel] = sha256_file(files[rel])
        changed = True
    if suite_coherent and suite_rel in files and suite_rel in updated:
        current = sha256_file(files[suite_rel])
        if updated[suite_rel] != current:
            updated[suite_rel] = current
            changed = True
    if changed:
        write_manifest(root, updated)
    return safe, []
