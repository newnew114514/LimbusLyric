#!/usr/bin/env python3
from __future__ import annotations
import ast
import pathlib
import sys

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_STARTUP_REENTRY_CLOSURE_H95F4F1_REPLAY.py <main.py>')
path = pathlib.Path(sys.argv[1]).resolve()
src = path.read_text(encoding='utf-8')
tree = ast.parse(src)

def need(cond, message):
    if not cond:
        raise AssertionError(message)

marker = '# H95F4F1 startup re-entry closure'
need(marker in src, 'H95F4F1 marker missing')
need('+ STARTUP REENTRY CLOSURE H95F4F1' in src, 'H95F4F1 build tag missing')
start = src.index(marker)
end = src.index('if __name__ == "__main__":', start)
block = src[start:end]
need("_h95f4_frontend_apply_guard" in block, 're-entry guard missing')
need("globals()['_h95f4_apply_frontend'] = _h95f4f1_apply_frontend" in block, 'guarded applicator not activated')
need('finally:' in block and "panel._h95f4_frontend_apply_guard = False" in block, 'guard is not exception-safe')

fn = next((node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == '_h95f4f1_apply_frontend'), None)
need(fn is not None, 'guarded applicator function missing')

class Panel:
    _h95f4_frontend_version = 'studio'

panel = Panel()
ns = {
    '_h95f4_frontend_value': lambda p: getattr(p, '_h95f4_frontend_version', 'studio'),
}
exec(compile(ast.Module(body=[fn], type_ignores=[]), '<h95f4f1>', 'exec'), ns)
calls = []

def recursive_pre(p, mode=None, save=False):
    calls.append((mode, save, bool(getattr(p, '_h95f4_frontend_apply_guard', False))))
    # Reproduce the H95F4 -> H95F3 Studio -> global H95F1 density -> H95F4 apply edge.
    nested = ns['_h95f4f1_apply_frontend'](p, mode, False)
    need(nested == mode, 'nested re-entry did not coalesce to normalized mode')
    return mode

ns['_H95F4F1_APPLY_FRONTEND_PRE'] = recursive_pre
result = ns['_h95f4f1_apply_frontend'](panel, 'legacy', False)
need(result == 'legacy', 'outer frontend application result changed')
need(len(calls) == 1, f're-entry guard failed; underlying applicator called {len(calls)} times')
need(calls[0][2] is True, 'underlying applicator did not run inside guarded transaction')
need(getattr(panel, '_h95f4_frontend_apply_guard', None) is False, 'guard not cleared after normal return')

# Exception path must also clear the guard so a later resize/theme change can recover.
def raising_pre(p, mode=None, save=False):
    raise RuntimeError('synthetic startup failure')
ns['_H95F4F1_APPLY_FRONTEND_PRE'] = raising_pre
try:
    ns['_h95f4f1_apply_frontend'](panel, 'studio', False)
except RuntimeError:
    pass
else:
    raise AssertionError('underlying failure was unexpectedly swallowed by guard wrapper')
need(getattr(panel, '_h95f4_frontend_apply_guard', None) is False, 'guard not cleared after exception')

print('STARTUP REENTRY CLOSURE H95F4F1 REPLAY: PASS')
print('  nested H95F4/H95F3 density re-entry coalesced: PASS')
print('  guard clears on success and exception: PASS')
