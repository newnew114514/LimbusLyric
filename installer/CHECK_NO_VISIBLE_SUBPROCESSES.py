from __future__ import annotations
import ast
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("usage: CHECK_NO_VISIBLE_SUBPROCESSES.py <main.py>")
    raise SystemExit(2)

path = Path(sys.argv[1])
tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
failures = []
checked = 0

def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))

def literal_strings(node):
    out = []
    if isinstance(node, (ast.List, ast.Tuple)):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                out.append(elt.value.lower())
    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
        out.append(node.value.lower())
    return out

for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue
    fn = dotted(node.func)
    if fn not in {
        "subprocess.run", "subprocess.Popen", "subprocess.call",
        "subprocess.check_call", "subprocess.check_output"
    }:
        continue
    if not node.args:
        continue
    strings = literal_strings(node.args[0])
    if not any("tasklist" in s or "wmic" in s or "cmd.exe" in s or "powershell" in s for s in strings):
        continue
    checked += 1
    kw = {k.arg: k.value for k in node.keywords if k.arg}
    if "creationflags" not in kw:
        failures.append(f"line {node.lineno}: {fn} external console command has no creationflags")
        continue
    source = ast.unparse(kw["creationflags"]) if hasattr(ast, "unparse") else ""
    if "CREATE_NO_WINDOW" not in source and "0x08000000" not in source and "134217728" not in source:
        failures.append(
            f"line {node.lineno}: {fn} creationflags does not visibly include CREATE_NO_WINDOW"
        )

if failures:
    print("VISIBLE SUBPROCESS AUDIT: FAIL")
    for item in failures:
        print("  " + item)
    raise SystemExit(19)

print(f"VISIBLE SUBPROCESS AUDIT: PASS ({checked} guarded external-console call(s))")
