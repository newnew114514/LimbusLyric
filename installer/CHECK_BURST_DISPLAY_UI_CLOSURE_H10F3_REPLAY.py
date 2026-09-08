#!/usr/bin/env python3
from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_BURST_DISPLAY_UI_CLOSURE_H10F3_REPLAY.py <main.py>')
path = Path(sys.argv[1])
source = path.read_text(encoding='utf-8')
tree = ast.parse(source)

def method_source(cls_name, method):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method:
                    return ast.get_source_segment(source, item)
    raise AssertionError(f'missing {cls_name}.{method}')

def need(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print('  ' + msg + ': PASS')

init = method_source('ControlPanel', '__init__')
deps = method_source('ControlPanel', '_sync_advanced_dependencies')
tracking_changed = method_source('ControlPanel', '_on_precise_tracking_changed')
display_changed = method_source('ControlPanel', '_on_precise_display_mode_changed')
classic_dense = method_source('LyricWindow', '_classic_dense_pop')
classic_micro = method_source('LyricWindow', '_classic_micro_pop')
provider_dense = method_source('LyricWindow', '_provider_dense_pop')

need('BURST-DISPLAY UI CLOSURE H10F3' in source, 'H10F3 build tag present')
need('QLabel("显示方式：")' in init, 'burst selector is presented as a general display choice')
need('高速直出（仅快段）' in init, 'burst selector option remains available')
need('高速直出”在两种显示状态下都可独立使用' in init, 'precise checkbox tooltip documents classic compatibility')
need('关闭精准模式后，也可让经典连续显示中的高速片段直接弹出' in init, 'burst tooltip documents classic behavior')
need('precise_display_combo.setEnabled' not in deps, 'advanced dependency sync no longer disables burst selector')
need('precise_display_combo' not in tracking_changed and 'precise_display_mode' not in tracking_changed,
     'toggling precise tracking cannot reset or overwrite burst selection')
need("self.lyric_window.precise_display_mode = mode" in display_changed,
     'display selector remains an independent persisted presentation control')
need("precise_display_mode', 'word') or 'word') != 'burst'" in classic_dense and 'if not bool(getattr(self, \'precise_tracking_enabled\'' not in classic_dense,
     'classic fast-run burst remains available with precise tracking off')
need("precise_display_mode', 'word') or 'word') != 'burst'" in classic_micro and 'if not bool(getattr(self, \'precise_tracking_enabled\'' not in classic_micro,
     'classic tiny-unit burst remains available with precise tracking off')
need("if not bool(getattr(self, 'precise_tracking_enabled', True))" in provider_dense,
     'provider word-timed burst still requires precise tracking')

# Execute the real classic dense method with a minimal harness: classic+burst must admit,
# classic+word must not. No transport/seek/timing authority participates in this UI fix.
ns = {'DENSE_BURST_POP_ENABLED': True, 'FLOW_STACK_ENABLED': True}
body = textwrap.indent(classic_dense, '    ')
exec('class H:\n' + body, ns)
H = ns['H']
h = H(); h.lyric_timeline = [(0, 'a'), (300, 'b'), (600, 'c')]
h.precise_tracking_enabled = False
h._burst_run_member = lambda idx, provider=False: True
h.precise_display_mode = 'burst'
need(h._classic_dense_pop(0) is True, 'classic mode + burst selector activates existing fast-run direct output')
h.precise_display_mode = 'word'
need(h._classic_dense_pop(0) is False, 'classic mode + word selector keeps continuous presentation')

print('BURST DISPLAY UI CLOSURE H10F3 REPLAY: PASS')
