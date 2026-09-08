from pathlib import Path
import ast, sys
MAIN=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/"LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"
s=MAIN.read_text(encoding='utf-8')
need=[
 'DwmGetWindowAttribute', 'DWMWA_EXTENDED_FRAME_BOUNDS=9',
 "write_error_log('酷狗物理窗口坐标'",
 "write_error_log('酷狗鼠标物理坐标诊断'",
 "phase, 'capture-unavailable'" if False else "'capture-unavailable'",
 "'duration-unavailable'",
 "reason='user-rail-gesture', absolute=True",
 "position_source=\"kugou-rail-local-master\"",
 "learned = getattr(self, '_kugou_visual_rail_bounds', None)",
]
missing=[x for x in need if x not in s]
if missing:
 print('KUGOU PHYSICAL RAIL TRACKER REPLAY: FAIL missing',missing); raise SystemExit(61)
# Bootstrap/transport-local seeds must remain display continuity only and must not
# claim absolute position before a real Host/visual/gesture proof.  Do this as an
# AST semantic check rather than pinning one historical tuple spelling: H5/H7
# legitimately added transport-edge-local + identity-transport-local to the same guard.
provisional_reasons = {
 'manual-zero-bootstrap', 'auto-track-bootstrap', 'lazy-zero-bootstrap',
 'transport-edge-local', 'identity-transport-local',
}
for reason in provisional_reasons:
 if reason not in s:
  print('KUGOU PHYSICAL RAIL TRACKER REPLAY: FAIL missing provisional reason',reason); raise SystemExit(62)
tree=ast.parse(s)
seed_fn=None
for node in ast.walk(tree):
 if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name == '_kugou_seed_rail_local_master':
  seed_fn=node; break
if seed_fn is None:
 print('KUGOU PHYSICAL RAIL TRACKER REPLAY: FAIL seed function missing'); raise SystemExit(62)
def membership_values(test):
 vals=set()
 for node in ast.walk(test):
  if isinstance(node,ast.Compare) and isinstance(node.left,ast.Name) and node.left.id=='reason_text':
   for op,comp in zip(node.ops,node.comparators):
    if isinstance(op,ast.In) and isinstance(comp,(ast.Tuple,ast.List,ast.Set)):
     vals.update(x.value for x in comp.elts if isinstance(x,ast.Constant) and isinstance(x.value,str))
 return vals
def body_forces_nonabsolute(body):
 for node in ast.walk(ast.Module(body=body,type_ignores=[])):
  if isinstance(node,ast.Assign):
   if any(isinstance(t,ast.Name) and t.id=='absolute' for t in node.targets) and isinstance(node.value,ast.Constant) and node.value.value is False:
    return True
 return False
semantic_guard=False
for node in ast.walk(seed_fn):
 if isinstance(node,ast.If) and provisional_reasons.issubset(membership_values(node.test)) and body_forces_nonabsolute(node.body):
  semantic_guard=True; break
if not semantic_guard:
 print('KUGOU PHYSICAL RAIL TRACKER REPLAY: FAIL provisional non-absolute semantic guard missing'); raise SystemExit(62)
# The historical memory lane remains default-off.
if "LIMBUSLYRIC_KUGOU_NUMERIC_CLOCK', '0'" not in s:
 print('KUGOU PHYSICAL RAIL TRACKER REPLAY: FAIL numeric default'); raise SystemExit(63)
# Learned rail geometry must be used before coarse whole-window mapping.
li=s.index("learned = getattr(self, '_kugou_visual_rail_bounds', None)")
ri=s.index('ratio = (float(cx) - x0)',li)
assert li < ri
ast.parse(s)
print('KUGOU PHYSICAL RAIL TRACKER REPLAY: PASS')
