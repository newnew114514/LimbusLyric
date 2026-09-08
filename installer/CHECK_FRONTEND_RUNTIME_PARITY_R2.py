from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((Path(__file__).with_name('R2_FRONTEND_RUNTIME_BASELINE.json')).read_text(encoding='utf-8'))
rows = sorted(ROOT.glob('LimbusLyric_v1.8.9.133_CROSS_PROVIDER*.py'))
assert len(rows) == 1, rows
source = rows[0].read_text(encoding='utf-8')
tree = ast.parse(source)
current = {k: [] for k in BASELINE}
for node in ast.walk(tree):
    if not isinstance(node, ast.Assign):
        continue
    for target in node.targets:
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
            key = f'{target.value.id}.{target.attr}'
            if key in current:
                current[key].append(ast.unparse(node.value))

bad = []
for key, expected in BASELINE.items():
    got = current.get(key, [])
    if got != expected:
        bad.append((key, len(expected), len(got), expected, got))
if bad:
    print('FRONTEND RUNTIME PARITY R2: FAIL')
    for key, ne, ng, expected, got in bad:
        print(f'  {key}: expected {ne}, got {ng}')
        for i, (a, b) in enumerate(zip(expected, got)):
            if a != b:
                print(f'    first mismatch @{i}: expected={a} got={b}')
                break
    raise SystemExit(2)
print('FRONTEND RUNTIME PARITY R2: PASS ' + ' | '.join(f'{k}={len(v)}' for k, v in current.items()))
