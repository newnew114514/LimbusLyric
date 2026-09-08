from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
from SOURCE_MANIFEST import regenerate_manifest

if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_SOURCE_MANIFEST_AUTOSYNC_REPLAY.py <project-root>")
project = Path(sys.argv[1]).resolve()
sync = project / "installer" / "SYNC_SOURCE_MANIFEST_ADDITIONS.py"
checker = project / "installer" / "CHECK_PACKAGING_STRUCTURE.py"
main_name = "LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"


def manifest_line(path: Path, root: Path) -> str:
    return f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root).as_posix()}\n"


def run(script: Path, root: Path):
    return subprocess.run([sys.executable, str(script), str(root)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)

with tempfile.TemporaryDirectory(prefix="limbus-manifest-autosync-") as td:
    root = Path(td)
    inst = root / "installer"
    inst.mkdir(parents=True)
    main = root / main_name
    build = inst / "BUILD_RELEASE.cmd"
    suite = inst / "RELEASE_GATE_SUITE.tsv"
    main.write_text("print('fixture')\n", encoding="utf-8")
    build.write_text("@echo off\n", encoding="utf-8")
    suite.write_text("", encoding="utf-8")
    (root / "SHA256_FILES.txt").write_text(
        manifest_line(main, root) + manifest_line(build, root) + manifest_line(suite, root),
        encoding="utf-8",
    )


    # A maintainer full-refresh may happen after py_compile. Cache files are never payload.
    cache_dir = root / "__pycache__"
    cache_dir.mkdir()
    cache_file = cache_dir / "fixture.cpython-312.pyc"
    cache_file.write_bytes(b"bytecode-cache")
    regenerate_manifest(root)
    manifest_text = (root / "SHA256_FILES.txt").read_text(encoding="utf-8")
    assert "__pycache__" not in manifest_text and ".pyc" not in manifest_text, manifest_text
    cache_file.unlink(); cache_dir.rmdir()

    # Simulate a normal new Hxx patch: new replay + new note + suite registration.
    gate = inst / "CHECK_H99_REPLAY.py"
    note = root / "EXAMPLE_H99_NOTE_20990101.md"
    gate.write_text("print('H99')\n", encoding="utf-8")
    note.write_text("# H99\n", encoding="utf-8")
    suite.write_text("CHECK_H99_REPLAY.py\tmain\n", encoding="utf-8")
    proc = run(sync, root)
    assert proc.returncode == 0 and "auto-added=2" in proc.stdout, proc.stdout
    proc = run(checker, root)
    assert proc.returncode == 0, proc.stdout

    # Unknown source material must not be silently blessed.
    unknown = root / "mystery_payload.bin"
    unknown.write_bytes(b"mystery")
    proc = run(sync, root)
    assert proc.returncode != 0 and "not auto-enrolled" in proc.stdout, proc.stdout
    unknown.unlink()

    # Existing non-metadata manifest hashes remain immutable during safe-sync.
    build.write_text("@echo changed\n", encoding="utf-8")
    proc = run(sync, root)
    assert proc.returncode == 0, proc.stdout
    proc = run(checker, root)
    assert proc.returncode != 0 and "manifest hash mismatch" in proc.stdout, proc.stdout

print("SOURCE MANIFEST AUTOSYNC REPLAY: PASS")
print("  registered CHECK_* + NOTE/AUDIT additions are auto-enrolled")
print("  coherent RELEASE_GATE_SUITE.tsv hash refreshes automatically")
print("  unknown new payload remains fatal")
print("  existing non-metadata manifest hash mismatches are never auto-refreshed")
