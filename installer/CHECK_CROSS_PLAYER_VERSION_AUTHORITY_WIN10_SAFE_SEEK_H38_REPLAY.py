from pathlib import Path
import ast, sys

if len(sys.argv) != 2:
    raise SystemExit(2)
source_path = Path(sys.argv[1])
text = source_path.read_text(encoding='utf-8')

def need(cond, msg):
    if not cond:
        print('CROSS-PLAYER VERSION AUTHORITY + WIN10 SAFE SEEK H38 REPLAY: FAIL')
        print(' - ' + msg)
        raise SystemExit(1)

markers = [
    '+ CROSS-PLAYER VERSION AUTHORITY + WIN10 SAFE SEEK H38',
    'H38酷狗Win10歌词时长未获播放器授权',
    'H38酷狗Win10播放器时长视觉速率确认',
    'H38跨播放器同名版本时长冲突',
    'H38酷狗Seek后同曲Transport零点阻断',
    "_limbus_duration_policy = 'player-evidence-or-scale-free-visual-rate'",
    "_limbus_version_policy = 'same-title-version-provisional-until-player-duration'",
]
for marker in markers:
    need(marker in text, 'missing H38 marker: ' + marker)

# Pure policy helpers must remain executable without Qt/WinRT.
tree = ast.parse(text)
wanted_assign = {
    'H38_DURATION_CONFLICT_MIN_MS','H38_DURATION_CONFLICT_RATIO',
    'H38_KUGOU_VISUAL_DURATION_MIN_MS','H38_KUGOU_VISUAL_DURATION_MAX_MS',
    'H38_KUGOU_VISUAL_DURATION_MIN_SAMPLES','H38_KUGOU_VISUAL_DURATION_MIN_SPAN_MS',
    'H38_KUGOU_VISUAL_DURATION_REL_SPREAD','H38_KUGOU_POST_SEEK_ZERO_VETO_MS',
}
wanted_funcs = {
    '_h38_duration_conflict','_h38_visual_duration_estimate',
    '_h38_visual_duration_consensus','_h38_should_block_kugou_transport_zero',
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

conflict=ns['_h38_duration_conflict']
need(conflict(81000,221500), '81s KuGou lyric vs 221.5s player duration conflict was not detected')
need(conflict(81000,242000), '81s KuGou lyric vs 242s player duration conflict was not detected')
need(not conflict(221000,221500), 'near-identical provider/player durations were over-rejected')

estimate=ns['_h38_visual_duration_estimate']
# Wrong 81s scale advancing ~603ms over 1.8s corresponds to a real duration near 242s.
e=estimate(81000, {'hits':4,'span':1800.0,'advance':603.0})
need(e is not None and 238000 <= e <= 246000, f'scale-free visual rate did not recover ~242s: {e}')

consensus=ns['_h38_visual_duration_consensus']([
    {'duration_ms':241200,'mono':1000},
    {'duration_ms':243000,'mono':1700},
    {'duration_ms':242100,'mono':2400},
])
need(consensus is not None and 241000 <= consensus <= 243500, f'visual duration consensus failed: {consensus}')
need(ns['_h38_visual_duration_consensus']([
    {'duration_ms':180000,'mono':1000}, {'duration_ms':242000,'mono':1800}, {'duration_ms':330000,'mono':2600}
]) is None, 'widely disagreeing visual duration estimates were accepted')

block=ns['_h38_should_block_kugou_transport_zero']
need(block(10000,14500,True), 'same-track GSMTC zero within 4.5s of a user seek was not vetoed')
need(not block(10000,16000,True), 'transport zero was vetoed beyond the scoped H38 window')
need(not block(10000,12000,False), 'different-track transport reset was over-blocked')

need("row['duration'] = 0" in text and 'seek-scale=disabled' in text,
     'Win10 KuGou lyric-only duration is still allowed to become seek scale')
need("provider_duration_ms': duration" in text and 'duration-anchored-refetch' in text,
     'cross-player mismatch does not requery with player-owned duration')
probe_node = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == '_h38_probe_kugou_visual_duration')
probe_source = ast.get_source_segment(text, probe_node) or ''
need("or -1.0" not in probe_source,
     'valid zero gesture timestamp is treated as missing and resets H30 visual state every poll')

print('CROSS-PLAYER VERSION AUTHORITY + WIN10 SAFE SEEK H38 REPLAY: PASS')
print(' - lyric/KRC duration cannot authorize Win10 KuGou seek scale by itself')
print(' - physical rail velocity can infer total duration without unsafe UIA/MSAA')
print(' - cross-player same-title duration conflicts force a duration-anchored lyric refetch')
print(' - recent explicit KuGou seeks veto ambiguous same-identity GSMTC zero resets')
print(' - zero gesture baseline remains stable instead of restarting H30 every poll')
