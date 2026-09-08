from __future__ import annotations
import importlib.metadata as metadata
import platform
import sys

EXPECTED = {
    "PyQt5": "5.15.11",
    "pywin32": "311",
    "pywinauto": "0.6.9",
    "comtypes": "1.4.16",
    "pycaw": "20251023",
    "pyinstaller": "6.21.0",
}


def main() -> int:
    failures = []
    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python={py}")
    print(f"Platform={platform.platform()}")
    if sys.version_info[:2] != (3, 12):
        failures.append(f"Python 3.12.x required, got {py}")
    for package, expected in EXPECTED.items():
        try:
            actual = metadata.version(package)
        except Exception as exc:
            failures.append(f"{package}: not installed ({type(exc).__name__})")
            continue
        print(f"{package}={actual}")
        if actual != expected:
            failures.append(f"{package}: expected {expected}, got {actual}")
    if failures:
        print("BUILD RUNTIME PROFILE: FAIL")
        for item in failures:
            print(" -", item)
        return 1
    print("BUILD RUNTIME PROFILE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
