#!/usr/bin/env python3
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

MAIN_NAME = "LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"
GATE_SUITE_NAME = "RELEASE_GATE_SUITE.tsv"
DEFAULT_MAX_WORKERS = 8
WINDOWS_DEFAULT_MAX_WORKERS = 2
SPAWN_RETRY_DELAYS = (0.20, 0.60, 1.20)
DEFAULT_GATE_TIMEOUT_SECONDS = 120
VALID_MODES = {"main", "root", "root-main"}
PARTIAL_CACHE_SCHEMA = 1
PARTIAL_CACHE_NAME = ".release_gate_partial_cache.json"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _partial_cache_path(root: Path) -> Path:
    # Keep the cache inside the reusable build venv directory. It is excluded from
    # the release payload/manifest and therefore can never leak into the product.
    return root / ".build_installer_venv_ascii" / PARTIAL_CACHE_NAME


def _common_gate_fingerprint(root: Path) -> str:
    """Fingerprint audited inputs shared by all gates, excluding CHECK_*.py.

    A gate-only expectation fix must not invalidate 202 unrelated PASS results.
    Conversely, a source/runtime/helper/build-input change must invalidate every
    cached gate. SHA256_FILES.txt already gives us the canonical audited payload;
    hash every manifest row except the individual gate scripts, then bind the
    canonical suite declaration and runner semantics explicitly.
    """
    manifest = root / "SHA256_FILES.txt"
    h = hashlib.sha256()
    h.update(f"limbus-release-gate-partial-v{PARTIAL_CACHE_SCHEMA}\n".encode())
    if not manifest.is_file():
        raise RuntimeError(f"source manifest missing: {manifest}")
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            raise RuntimeError(f"invalid manifest row: {raw!r}")
        digest, rel = parts
        rel_norm = rel.replace("\\", "/")
        name = rel_norm.rsplit("/", 1)[-1]
        if rel_norm.startswith("installer/") and name.startswith("CHECK_") and name.endswith(".py"):
            continue
        h.update(digest.lower().encode("ascii"))
        h.update(b"  ")
        h.update(rel_norm.encode("utf-8"))
        h.update(b"\n")
    suite = root / "installer" / GATE_SUITE_NAME
    h.update(b"suite\0")
    h.update(_sha256_file(suite).encode("ascii"))
    # Python major/minor can change AST/runtime behavior even with identical source.
    h.update(f"\npy={sys.version_info.major}.{sys.version_info.minor}".encode("ascii"))
    return h.hexdigest()


def _load_partial_cache(root: Path, common_fingerprint: str) -> dict:
    path = _partial_cache_path(root)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        if data.get("schema") != PARTIAL_CACHE_SCHEMA:
            return {}
        if data.get("common_fingerprint") != common_fingerprint:
            return {}
        passes = data.get("passes")
        return passes if isinstance(passes, dict) else {}
    except Exception:
        return {}


def _write_partial_cache(root: Path, common_fingerprint: str, passes: dict) -> None:
    path = _partial_cache_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": PARTIAL_CACHE_SCHEMA,
        "common_fingerprint": common_fingerprint,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "passes": passes,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _gate_cache_signature(root: Path, name: str, mode: str) -> dict:
    script = root / "installer" / name
    return {"mode": mode, "script_sha256": _sha256_file(script)}


def discover_gates(root: Path):
    suite = root / "installer" / GATE_SUITE_NAME
    if not suite.is_file():
        raise RuntimeError(f"release gate suite missing: {suite}")
    gates = []
    seen = set()
    for lineno, raw in enumerate(suite.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            raise RuntimeError(f"invalid {GATE_SUITE_NAME}:{lineno}: expected script<TAB>mode")
        name, mode = (part.strip() for part in parts)
        if not name.startswith("CHECK_") or not name.endswith(".py"):
            raise RuntimeError(f"invalid release gate name at line {lineno}: {name}")
        if mode not in VALID_MODES:
            raise RuntimeError(f"invalid release gate mode at line {lineno}: {mode}")
        if name in seen:
            raise RuntimeError(f"duplicate release gate in {GATE_SUITE_NAME}: {name}")
        seen.add(name)
        gates.append((name, mode))
    if not gates:
        raise RuntimeError("canonical release gate suite is empty")
    return gates


def _kill_process_tree(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
            )
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
    try:
        proc.wait(timeout=5)
    except Exception:
        pass


def _select_gate_python() -> Path:
    # Release gates intentionally use only the Python standard library.  On Windows the
    # builder itself runs from a venv placed under a SUBST drive.  Re-spawning that venv
    # launcher dozens of times proved fragile on real machines: CreateProcess can start
    # returning WinError 2 even though the project and gate files still exist.  Prefer the
    # stable base interpreter backing the venv; keep sys.executable as a verified fallback.
    candidates = []
    base = getattr(sys, "_base_executable", None)
    if base:
        candidates.append(Path(base))
    candidates.append(Path(sys.executable))
    seen = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except Exception:
            resolved = candidate
        key = os.path.normcase(str(resolved))
        if key in seen:
            continue
        seen.add(key)
        if resolved.is_file():
            return resolved
    raise RuntimeError(
        "no usable Python interpreter for release gates; "
        f"base={base!r} executable={sys.executable!r}"
    )


def _spawn_gate(command, popen_kwargs, *, script: Path, cwd: Path, gate_python: Path):
    errors = []
    attempts = 1 + len(SPAWN_RETRY_DELAYS)
    for attempt in range(attempts):
        try:
            return subprocess.Popen(command, **popen_kwargs), errors
        except FileNotFoundError as exc:
            errors.append(repr(exc))
            # If one of the actual inputs disappeared, retries would only hide a real
            # packaging fault.  Otherwise treat WinError 2 as a transient CreateProcess
            # failure and retry with a short backoff.
            missing = []
            if not gate_python.is_file():
                missing.append(f"python={gate_python}")
            if not script.is_file():
                missing.append(f"script={script}")
            if not cwd.is_dir():
                missing.append(f"cwd={cwd}")
            if missing or attempt >= attempts - 1:
                detail = ", ".join(missing) if missing else "all paths still exist"
                raise FileNotFoundError(
                    f"gate spawn failed after {attempt + 1}/{attempts} attempt(s); "
                    f"{detail}; python={gate_python}; script={script}; cwd={cwd}; "
                    f"errors={' | '.join(errors)}"
                ) from exc
            time.sleep(SPAWN_RETRY_DELAYS[attempt])


def _run_gate(index: int, total: int, root: Path, main: Path, name: str, mode: str, env: dict, gate_timeout: int, gate_python: Path):
    script = root / "installer" / name
    if not script.is_file():
        return index, name, 127, "gate script missing", False
    args = []
    if mode == "main":
        args = [str(main)]
    elif mode == "root":
        args = [str(root)]
    elif mode == "root-main":
        args = [str(root), str(main)]
    cwd = root / "installer"
    popen_kwargs = dict(cwd=str(cwd), env=env, stderr=subprocess.STDOUT)
    if os.name == "nt":
        popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        popen_kwargs["start_new_session"] = True
    with tempfile.TemporaryFile(mode="w+b") as capture:
        popen_kwargs["stdout"] = capture
        proc, spawn_errors = _spawn_gate(
            [str(gate_python), str(script), *args], popen_kwargs,
            script=script, cwd=cwd, gate_python=gate_python,
        )
        timed_out = False
        try:
            code = proc.wait(timeout=gate_timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_process_tree(proc)
            code = 124
        capture.seek(0)
        output = capture.read().decode("utf-8", errors="replace")
    if spawn_errors:
        output = f"gate spawn recovered after {len(spawn_errors)} FileNotFoundError retry/retries\n" + output
    if timed_out:
        output += f"\nTIMEOUT after {gate_timeout}s (process tree terminated)\n"
    return index, name, int(code), output, timed_out


def run_suite(root: Path, main: Path) -> int:
    gates = discover_gates(root)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    platform_default_workers = WINDOWS_DEFAULT_MAX_WORKERS if os.name == "nt" else DEFAULT_MAX_WORKERS
    try:
        requested_workers = int(os.environ.get("LIMBUSLYRIC_GATE_WORKERS", str(platform_default_workers)) or platform_default_workers)
    except Exception:
        requested_workers = platform_default_workers
    try:
        gate_timeout = int(os.environ.get("LIMBUSLYRIC_GATE_TIMEOUT", str(DEFAULT_GATE_TIMEOUT_SECONDS)) or DEFAULT_GATE_TIMEOUT_SECONDS)
    except Exception:
        gate_timeout = DEFAULT_GATE_TIMEOUT_SECONDS
    workers = min(max(1, requested_workers), 32, len(gates))
    gate_timeout = min(max(15, gate_timeout), 600)
    gate_python = _select_gate_python()
    partial_cache_enabled = str(os.environ.get("LIMBUSLYRIC_GATE_PARTIAL_CACHE", "1")).strip().lower() not in {"0", "false", "no", "off"}
    force_gates = str(os.environ.get("LIMBUSLYRIC_FORCE_GATES", "0")).strip().lower() in {"1", "true", "yes", "on"}
    common_fingerprint = ""
    cached_passes = {}
    gate_signatures = {}
    reusable = {}
    if partial_cache_enabled and not force_gates:
        try:
            common_fingerprint = _common_gate_fingerprint(root)
            cached_passes = _load_partial_cache(root, common_fingerprint)
            for i, (name, mode) in enumerate(gates, 1):
                signature = _gate_cache_signature(root, name, mode)
                gate_signatures[name] = signature
                if cached_passes.get(name) == signature:
                    reusable[i] = name
        except Exception as exc:
            print(f"RELEASE GATE PARTIAL CACHE: disabled for this run ({exc})", flush=True)
            common_fingerprint = ""
            cached_passes = {}
            gate_signatures = {}
            reusable = {}
    elif force_gates:
        print("RELEASE GATE PARTIAL CACHE: bypassed by LIMBUSLYRIC_FORCE_GATES=1", flush=True)

    print(
        f"RELEASE GATE SUITE: {len(gates)} canonical gate(s); workers={workers}; "
        f"timeout={gate_timeout}s/gate; gate-python={gate_python}; cached-pass={len(reusable)}",
        flush=True,
    )
    failures = []
    for i, name in sorted(reusable.items()):
        print(f"[{i:02d}/{len(gates):02d}] PASS {name} (cached)", flush=True)

    pending = [
        (i, name, mode)
        for i, (name, mode) in enumerate(gates, 1)
        if i not in reusable
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {
            pool.submit(_run_gate, i, len(gates), root, main, name, mode, env, gate_timeout, gate_python): (i, name)
            for i, name, mode in pending
        }
        for future in concurrent.futures.as_completed(future_map):
            i, expected_name = future_map[future]
            try:
                result = future.result()
            except Exception as exc:
                result = (i, expected_name, 125, f"gate-runner exception: {exc!r}\n", False)
            index, name, code, output, timed_out = result
            # Successful gate chatter is redundant with the PASS line and can contain
            # provider text that some Windows PTYs cannot safely echo. Keep full output
            # only where it is actionable.
            if output and code:
                print(f"--- {name} output ---", flush=True)
                print(output, end="" if output.endswith("\n") else "\n", flush=True)
            if code:
                failures.append(result)
                suffix = " TIMEOUT" if timed_out else f" exit={code}"
                print(f"[{index:02d}/{len(gates):02d}] FAIL {name}{suffix}", flush=True)
            else:
                print(f"[{index:02d}/{len(gates):02d}] PASS {name}", flush=True)
                if partial_cache_enabled and not force_gates and common_fingerprint:
                    try:
                        signature = gate_signatures.get(name) or _gate_cache_signature(root, name, dict(gates)[name])
                        gate_signatures[name] = signature
                        cached_passes[name] = signature
                        _write_partial_cache(root, common_fingerprint, cached_passes)
                    except Exception as exc:
                        print(f"  warning: could not persist partial PASS cache for {name}: {exc}", flush=True)
    print("=" * 68, flush=True)
    if failures:
        print(f"RELEASE GATE SUITE: FAIL ({len(failures)}/{len(gates)})", flush=True)
        for index, name, code, output, timed_out in sorted(failures):
            tail = " | ".join(line.strip() for line in output.splitlines()[-3:] if line.strip())
            label = "timeout" if timed_out else f"exit={code}"
            print(f"  - {name}: {label}" + (f" | {tail}" if tail else ""), flush=True)
        print("All gate failures above were collected in one run; no first-failure masking.", flush=True)
        return 1
    print(f"RELEASE GATE SUITE: PASS ({len(gates)}/{len(gates)})", flush=True)
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) not in (1, 2):
        raise SystemExit("usage: RUN_RELEASE_GATE_SUITE.py <root> [main.py]")
    root = Path(argv[0]).resolve()
    main_path = Path(argv[1]).resolve() if len(argv) == 2 else root / MAIN_NAME
    raise SystemExit(run_suite(root, main_path))


if __name__ == "__main__":
    main()
