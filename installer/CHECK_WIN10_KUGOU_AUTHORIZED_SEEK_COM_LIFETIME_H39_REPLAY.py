from pathlib import Path
import ast, sys

if len(sys.argv) != 2:
    raise SystemExit(2)
source_path = Path(sys.argv[1])
text = source_path.read_text(encoding='utf-8')

def need(cond, msg):
    if not cond:
        print('WIN10 KUGOU AUTHORIZED SEEK + COM LIFETIME H39 REPLAY: FAIL')
        print(' - ' + msg)
        raise SystemExit(1)

markers = [
    '+ WIN10 KUGOU AUTHORIZED SEEK + COM LIFETIME H39',
    'H39酷狗Win10未授权Seek延迟接管',
    'H39 Win10进程级循环GC保护',
    "_limbus_win10_seek_duration = 'h38-player-owned-only'",
    "_limbus_seek_authority = 'player-owned-duration-required-on-win10'",
    "_limbus_gc_policy = 'win10-frozen-process-cyclic-gc-disabled'",
    "_limbus_ncm_refetch_policy = 'refresh-accepted-duration-metadata'",
]
for marker in markers:
    need(marker in text, 'missing H39 marker: ' + marker)

tree = ast.parse(text)
wanted_assign = {'H39_KUGOU_MIN_AUTHORIZED_DURATION_MS'}
wanted_funcs = {
    '_h39_select_kugou_seek_duration',
    '_h39_should_hold_process_gc_disabled',
    '_h39_kugou_ratio_from_untrusted_target',
}
nodes=[]
for node in tree.body:
    if isinstance(node, ast.Assign):
        names={t.id for t in node.targets if isinstance(t, ast.Name)}
        if names & wanted_assign:
            nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in wanted_funcs:
        nodes.append(node)
ns={'math':__import__('math')}
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source_path),'exec'),ns)

pick=ns['_h39_select_kugou_seek_duration']
need(pick(True, 0, 221000, 221000) == 0,
     'Win10 still accepts lyric/UI/state duration when no H38 player-owned duration exists')
need(pick(True, 230963, 221000, 221000) == 230963,
     'Win10 did not prefer the independently player-owned duration')
need(pick(False, 0, 221000, 0) == 221000,
     'non-Win10 pass-through duration behavior was over-restricted')

ratio=ns['_h39_kugou_ratio_from_untrusted_target'](44590,221000)
need(ratio is not None and abs(ratio-(44590/221000)) < 1e-9,
     'physical gesture ratio cannot be preserved while refusing the untrusted time scale')
need(ns['_h39_kugou_ratio_from_untrusted_target'](1000,0) is None,
     'zero-duration gesture unexpectedly produced a ratio')

gc_guard=ns['_h39_should_hold_process_gc_disabled']
need(gc_guard(19045,True,'1'), 'Win10 frozen process GC guard was not enabled')
need(not gc_guard(22631,True,'1'), 'Win11 was incorrectly placed under the Win10 process GC guard')
need(not gc_guard(19045,False,'1'), 'source/non-frozen Win10 was incorrectly forced into process GC guard')
need(not gc_guard(19045,True,'0'), 'explicit H39 GC opt-out was ignored')

# The runtime closure must execute before QApplication enters app.exec().
need(text.index("if '_h39_activate_runtime' in globals():") < text.index('if __name__ == "__main__":'),
     'H39 process GC guard activates too late (after main/event-loop entry)')
need("return None\n                rect = rect or" in text,
     'H39 target mapper does not fail closed before host-geometry scaling')
need("commit=blocked | wait=player-owned-duration" in text,
     'unowned KuGou gesture is not explicitly held instead of committed')
need("panel._h38_loaded_candidate_duration_ms = duration" in text and
     "panel._h38_loaded_candidate_track = key" in text,
     'NetEase accepted payload does not refresh H38 reconciliation metadata')

print('WIN10 KUGOU AUTHORIZED SEEK + COM LIFETIME H39 REPLAY: PASS')
print(' - Win10 KuGou rail target/commit requires H38 player-owned duration')
print(' - unowned clicks preserve only physical ratio and wait for player evidence')
print(' - Win10 frozen cyclic GC is disabled before Qt native dispatch; Win11 unchanged')
print(' - accepted NetEase payload refreshes reconciliation metadata to avoid repeat refetch')
