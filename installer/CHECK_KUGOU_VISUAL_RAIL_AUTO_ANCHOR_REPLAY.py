from pathlib import Path
import ast, sys
MAIN=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/"LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"
src=MAIN.read_text(encoding="utf-8")
need=[
 "KUGOU_VISUAL_RAIL_AUTO_ANCHOR_ENABLED",
 "def _kugou_capture_visual_strip",
 "def _kugou_visual_motion_candidate",
 "def _kugou_visual_infer_bounds",
 "def _kugou_poll_visual_rail_anchor",
 "reason='visual-rail-auto'",
 "screen-readonly=1",
 "self._kugou_poll_visual_rail_anchor(status_hint=effective, local_position_hint=value)",
 "global KUGOU_GESTURE_X_MIN, KUGOU_GESTURE_X_MAX",
]
missing=[x for x in need if x not in src]
if missing:
 print('KUGOU VISUAL RAIL AUTO ANCHOR REPLAY: FAIL missing',missing); raise SystemExit(41)
# Mirror the temporal gate numerically: a true rail at 1x survives; static/fast animation does not.
def coherent(prev_pos,pos,dt,duration,rail_w):
 dp=pos-prev_pos; tol=max(420.0,dt*0.72,duration/max(80.0,float(rail_w))*1.8)
 return dp>=-tol*0.20 and abs(dp-dt)<=tol
assert all(coherent(40000+i*320,40000+(i+1)*320,320,221000,520) for i in range(4))
assert not coherent(40000,40000,900,221000,520)
assert not coherent(40000,47000,320,221000,520)
# Learned geometry must replace whole-window 5.5/94.5 mapping when available.
x0,x1=280.0,760.0; dur=221000.0
target=(520-x0)/(x1-x0)*dur
assert 110000 < target < 111000
ast.parse(src)
print('KUGOU VISUAL RAIL AUTO ANCHOR REPLAY: PASS')
