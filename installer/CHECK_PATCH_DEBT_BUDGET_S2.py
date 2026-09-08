#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from collections import Counter, defaultdict
from pathlib import Path

BUDGETS = {
    'LyricSearchEngine.search': 5,
    'MediaSessionSync.snapshot': 4,
    'MediaSessionSync.bind_track': 6,
    'LyricWindow.paintEvent': 10,
    'ControlPanel.__init__': 54,
    'ControlPanel._on_auto_lyric_result': 14,
    'LyricWindow._make_history_line': 18,
    'FadingLine.draw': 17,
}


def scan(path: Path):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    counts = Counter()
    lines = defaultdict(list)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                    key = f'{target.value.id}.{target.attr}'
                    counts[key] += 1
                    lines[key].append(node.lineno)
        elif (
            isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'setattr'
            and len(node.args) >= 2 and isinstance(node.args[0], ast.Name)
            and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str)
        ):
            key = f'{node.args[0].id}.{node.args[1].value}'
            counts[key] += 1
            lines[key].append(node.lineno)
    return counts, lines


def main(argv):
    if len(argv) != 2:
        raise SystemExit('usage: CHECK_PATCH_DEBT_BUDGET_S2.py <main.py>')
    path = Path(argv[1]).resolve()
    counts, lines = scan(path)
    failures = []
    for key, budget in BUDGETS.items():
        count = int(counts.get(key, 0))
        if count > budget:
            failures.append((key, count, budget, lines.get(key, [])))
    if failures:
        print('PATCH DEBT BUDGET S2: FAIL')
        for key, count, budget, locs in failures:
            print(f'  {key}: {count}>{budget} lines={locs}')
        print('New runtime layers on these hotspots are forbidden; consolidate/remove an old layer first.')
        return 1
    print('PATCH DEBT BUDGET S2: PASS')
    for key, budget in BUDGETS.items():
        print(f'  {key}: {counts.get(key,0)}/{budget}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
