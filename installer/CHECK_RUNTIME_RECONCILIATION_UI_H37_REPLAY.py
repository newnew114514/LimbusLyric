from pathlib import Path
import ast, sys

if len(sys.argv) != 2:
    raise SystemExit(2)
source_path = Path(sys.argv[1])
text = source_path.read_text(encoding='utf-8')

def need(cond, msg):
    if not cond:
        print('RUNTIME RECONCILIATION + UI RECOVERY H37 REPLAY: FAIL')
        print(' - ' + msg)
        raise SystemExit(1)

markers = [
    '+ RUNTIME RECONCILIATION + UI RECOVERY H37',
    'H37紧急历史弹幕动态保留',
    'H37 QQ后台迟到UIA小回拨阻断',
    'H37酷狗Win10稳定Rail Seek',
    'H37酷狗Win10非Rail鼠标过滤',
    "_limbus_win10_negative_policy='psapi-positive-fast+8s-expensive-negative-backoff'",
    "_limbus_button_geometry='40x30-boxed-balanced-glyphs'",
]
for marker in markers:
    need(marker in text, 'missing H37 marker: ' + marker)
need("shakes = list(getattr(row, 'char_shakes'" in text, 'emergency history no longer reads living shake state')
need("scales = list(getattr(row, 'glyph_scales'" in text, 'emergency history no longer reads glyph scale state')
need("bar.min_btn.setText('−')" in text and "bar.max_btn.setText('▢')" in text and "bar.close_btn.setText('×')" in text,
     'balanced titlebar glyphs missing')

# Extract pure H37 policy helpers.
tree = ast.parse(text)
wanted_assign = {
    'H37_QQ_BACKGROUND_REWIND_MIN_MS','H37_QQ_BACKGROUND_REWIND_MAX_MS',
    'H37_KUGOU_WIN10_RAIL_TOLERANCE_PX'
}
wanted_funcs = {
    '_h37_kugou_seek_geometry_from_rect','_h37_kugou_seek_target_from_geometry',
    '_h37_should_block_qq_background_rewind'
}
nodes=[]
for node in tree.body:
    if isinstance(node, ast.Assign):
        names={t.id for t in node.targets if isinstance(t, ast.Name)}
        if names & wanted_assign:
            nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in wanted_funcs:
        nodes.append(node)
ns={}
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source_path),'exec'),ns)

geom=ns['_h37_kugou_seek_geometry_from_rect']((226,-1,1286,679))
need(geom is not None, 'Win10 KuGou host geometry helper returned None')
x0,x1,y=geom
need(abs(x0-263.1)<1.0 and abs(x1-1248.9)<1.0 and abs(y-607.6)<1.0,
     f'Win10 KuGou stable rail geometry drifted: {geom}')
target=ns['_h37_kugou_seek_target_from_geometry'](356,221000,geom)
need(target is not None and 20000 <= target <= 22000,
     f'Win10 KuGou cursor x=356 should map near 20.9s, got {target}')

block=ns['_h37_should_block_qq_background_rewind']
need(block(27000,33138,'playing',recent_invalid_window=True,click_evidence=False,lyric_evidence=False),
     'observed Win11 QQ 27s vs 33.1s late-background rewind is not blocked')
need(not block(27000,33138,'playing',recent_invalid_window=False,click_evidence=False,lyric_evidence=False),
     'ordinary unarmed QQ seek was over-blocked without recent invalid-window evidence')
need(not block(27000,33138,'playing',recent_invalid_window=True,click_evidence=True,lyric_evidence=False),
     'click-backed QQ seek was over-blocked')
need(not block(1000,25000,'playing',recent_invalid_window=True,click_evidence=False,lyric_evidence=False),
     'large QQ backward seek was over-blocked')

print('RUNTIME RECONCILIATION + UI RECOVERY H37 REPLAY: PASS')
print(' - emergency history preserves shake and glyph-scale motion under the fuse')
print(' - Win10 KuGou seek maps from stable Host geometry, independent of noisy visual rail bounds')
print(' - recent minimized-window QQ stale streams cannot manufacture a modest backward seek')
print(' - Win10 negative liveness backoff and restored titlebar button proportions are installed')
