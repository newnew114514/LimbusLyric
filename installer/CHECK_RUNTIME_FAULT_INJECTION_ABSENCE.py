#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit('usage: CHECK_RUNTIME_FAULT_INJECTION_ABSENCE.py <root> <main.py>')

root = Path(sys.argv[1]).resolve()
main = Path(sys.argv[2]).resolve()

def need(cond, msg):
    if not cond:
        print('RUNTIME TEST ISOLATION: FAIL ' + msg)
        raise SystemExit(1)
    print('  ' + msg + ': PASS')

source = main.read_text(encoding='utf-8')
tree = ast.parse(source, filename=str(main))

# Fault injection is a release-time replay only. Runtime source must not import/call it,
# expose a hidden switch for it, or embed the injected delay fixtures.
forbidden_runtime_tokens = (
    'CHECK_GUI_HOTPATH_FAULT_INJECTION_REPLAY',
    'FAULT_INJECTION',
    'FAULT-INJECTION CLOSURE',
    'injected process lookup delays',
    'nominal 5s Atlas build',
    'fault injector actually creates',
)
for token in forbidden_runtime_tokens:
    need(token not in source, f'runtime source excludes test token {token!r}')

imports = []
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imports.extend(alias.name for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        imports.append(node.module or '')
need(not any(name.startswith('installer') or 'CHECK_GUI_HOTPATH' in name for name in imports),
     'runtime imports no installer/check module')

# No environment/argv trigger may enable a hidden injection path in production.
hidden_trigger_strings = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        value = node.value.upper().replace('-', '_')
        if 'FAULT_INJECT' in value or 'INJECT_DELAY' in value:
            hidden_trigger_strings.append(node.value)
need(not hidden_trigger_strings, 'runtime contains no hidden fault-injection trigger string')

# The ordinary startup chain must lead only to the real main program. Build/test commands
# may run release gates, but user-facing launchers may never do so.
startup_files = (
    'START_HERE.cmd', 'LimbusLyric_START.cmd', 'RUN_CURRENT.cmd',
    'RUN_WITH_EXISTING_BETTERNCM_BRIDGE.cmd', 'TOOLS_ADVANCED.cmd',
)
for rel in startup_files:
    p = root / rel
    need(p.is_file(), f'startup file exists: {rel}')
    body = p.read_text(encoding='utf-8', errors='ignore').upper()
    need('CHECK_GUI_HOTPATH_FAULT_INJECTION_REPLAY' not in body,
         f'{rel} cannot invoke fault replay')
    need('RUN_RELEASE_GATE_SUITE' not in body,
         f'{rel} cannot invoke release-gate suite')

# PyInstaller includes MAIN + ordinary dependency data only; installer checks are not bundled
# into the end-user frozen application.
spec = (root/'installer'/'LimbusLyric.spec').read_text(encoding='utf-8', errors='ignore')
need('CHECK_GUI_HOTPATH_FAULT_INJECTION_REPLAY' not in spec, 'PyInstaller spec excludes fault replay script')
need(not re.search(r"datas\s*=.*installer", spec, flags=re.I|re.S), 'PyInstaller datas do not bundle installer tree')
need("[str(MAIN)]" in spec, 'PyInstaller analysis entry is canonical main source')

# The replay itself remains present as a test-only release gate so future regressions are
# still attacked before packaging.
replay = root/'installer'/'CHECK_GUI_HOTPATH_FAULT_INJECTION_REPLAY.py'
need(replay.is_file(), 'fault replay remains test-only under installer')
suite = (root/'installer'/'RELEASE_GATE_SUITE.tsv').read_text(encoding='utf-8', errors='ignore')
need('CHECK_GUI_HOTPATH_FAULT_INJECTION_REPLAY.py\tmain' in suite,
     'fault replay runs during release validation')
need('RUNTIME-ISOLATION CLOSURE H8F2' in source, 'H8F2 runtime-isolation marker present')

print('RUNTIME TEST ISOLATION: PASS')
