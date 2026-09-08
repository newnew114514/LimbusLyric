from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("usage: CHECK_PACKAGING_BUILD_ARTIFACT_ISOLATION_REPLAY.py <project-root>")

project = Path(sys.argv[1]).resolve()
checker = project / "installer" / "CHECK_PACKAGING_STRUCTURE.py"
main_name = "LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"


def write_manifest(root: Path) -> None:
    payload = [root / main_name, root / "installer" / "BUILD_RELEASE.cmd"]
    lines = []
    for path in payload:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(root).as_posix()}")
    (root / "SHA256_FILES.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(checker), str(root)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


with tempfile.TemporaryDirectory(prefix="limbus-packaging-policy-") as td:
    root = Path(td)
    (root / "installer").mkdir(parents=True)
    (root / main_name).write_text("print('fixture')\n", encoding="utf-8")
    (root / "installer" / "BUILD_RELEASE.cmd").write_text("@echo off\n", encoding="utf-8")
    write_manifest(root)

    # Every path below is expected to be created by build/runtime tooling and
    # must never be interpreted as canonical source payload.
    artifacts = {
        ".build_installer_venv_ascii/Lib/site-packages/pkg/__pycache__/pkg.cpython-312.pyc": b"pyc",
        ".build_installer_venv_ascii/Scripts/__pycache__/tool.pyc": b"pyc",
        ".pyinstaller_work/LimbusLyric/xref-LimbusLyric.html": b"work",
        "dist/LimbusLyric/LimbusLyric.exe": b"exe",
        "build/temporary.bin": b"build",
        "installer/release/LimbusLyric_Setup.exe": b"setup",
        "installer/release/LimbusLyric_Portable.zip": b"zip",
        "installer/offline_cache/wheels/example.whl": b"wheel",
        "installer/PACKAGING_SMOKE_RESULT.txt": b"PASS",
        "logs/LimbusLyric_session.log": b"log",
        ".pytest_cache/v/cache/nodeids": b"cache",
        ".git/objects/aa/bb": b"git",
    }
    for rel, data in artifacts.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    proc = run_checker(root)
    assert proc.returncode == 0, proc.stdout

    # A cache artifact in actual project source must still be rejected.
    bad = root / "project_pkg" / "__pycache__" / "bad.cpython-312.pyc"
    bad.parent.mkdir(parents=True)
    bad.write_bytes(b"bad")
    proc = run_checker(root)
    assert proc.returncode != 0 and "python cache artifacts present" in proc.stdout, proc.stdout
    bad.unlink()
    bad.parent.rmdir()
    bad.parent.parent.rmdir()

    # Unknown, non-declared output must not be silently hidden; manifest coverage
    # must catch it so the exclusion policy cannot grow into a blanket bypass.
    unknown = root / "mystery_output" / "unexpected.bin"
    unknown.parent.mkdir()
    unknown.write_bytes(b"unexpected")
    proc = run_checker(root)
    assert proc.returncode != 0 and "manifest coverage mismatch" in proc.stdout, proc.stdout

print("PACKAGING BUILD-ARTIFACT ISOLATION REPLAY: PASS")
print("  build venv / PyInstaller work / dist / build / installer release / offline cache / smoke / logs ignored")
print("  real project-source __pycache__ remains fatal")
print("  unknown undeclared output remains fatal via manifest coverage")
