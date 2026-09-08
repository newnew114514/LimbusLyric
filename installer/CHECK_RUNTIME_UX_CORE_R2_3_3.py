from pathlib import Path
import ast, sys
root=Path(sys.argv[1]).resolve()
main=next(root.glob('LimbusLyric_v1.8.9.133_*.py'))
src=main.read_text(encoding='utf-8')
tree=ast.parse(src)

def need(c,m):
    if not c:
        print('RUNTIME UX CORE R2.3.3: FAIL '+m)
        raise SystemExit(31)

# Field log exposed a real runtime NameError in both region preview paint paths.
# py_compile cannot catch missing global names, so explicitly resolve the QtGui import.
qtgui_imports=set()
for node in tree.body:
    if isinstance(node, ast.ImportFrom) and node.module=='PyQt5.QtGui':
        for alias in node.names:
            qtgui_imports.add(alias.asname or alias.name)
need('QPalette' in qtgui_imports,'QPalette is not imported from PyQt5.QtGui')

# There are exactly two intended QPalette consumers: the legacy R22 region preview and compact R23 preview.
qpal_uses=[n for n in ast.walk(tree) if isinstance(n,ast.Name) and n.id=='QPalette' and isinstance(n.ctx,ast.Load)]
covered_qpal_uses=0
for cls_name in ('R22RegionPreview','R23RegionMiniPreview'):
    cls=next((n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls_name),None)
    need(cls is not None,f'{cls_name} missing')
    paint=next((n for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=='paintEvent'),None)
    need(paint is not None,f'{cls_name}.paintEvent missing')
    local_uses=[n for n in ast.walk(paint) if isinstance(n,ast.Name) and n.id=='QPalette' and isinstance(n.ctx,ast.Load)]
    need(local_uses,f'{cls_name}.paintEvent no longer exercises QPalette guard')
    covered_qpal_uses += len(local_uses)
need(qpal_uses and covered_qpal_uses==len(qpal_uses),f'QPalette has unresolved/unreviewed consumers: total={len(qpal_uses)} reviewed={covered_qpal_uses}')

# Keep the hotfix surgically scoped: no runtime wrapper topology changes.
def count_attr_assign(owner,attr):
    n=0
    for node in ast.walk(tree):
        if not isinstance(node,ast.Assign): continue
        for t in node.targets:
            if isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id==owner and t.attr==attr:
                n+=1
    return n
for owner,attr,count in (
    ('ControlPanel','__init__',54),('LyricWindow','paintEvent',10),('FadingLine','draw',17),
    ('LyricWindow','_make_history_line',18),('LyricSearchEngine','search',5),
    ('MediaSessionSync','bind_track',6),('MediaSessionSync','snapshot',4)):
    need(count_attr_assign(owner,attr)==count,f'{owner}.{attr} topology changed')

print('RUNTIME UX CORE R2.3.3: PASS')
print('  QPalette resolves for both region-preview paint paths')
print('  preview/player/renderer wrapper topology unchanged')
