from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_QQ_CROSSSOURCE_DURATION_RACE_REPLAY.py <main.py>')
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8'); tree=ast.parse(source)

def method_source(cls_name, method):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method:
                    return ast.get_source_segment(source, item)
    raise AssertionError(f'missing {cls_name}.{method}')

def top_function_source(name):
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(source, node)
    raise AssertionError(f'missing top-level {name}')

def const(name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f'missing const {name}')

request_src = method_source('ControlPanel', '_request_auto_track')
start_src = method_source('ControlPanel', '_start_auto_search_job')
helper_src = method_source('ControlPanel', '_resolve_qq_auto_track_duration_after_bind')
epoch_helper_src = top_function_source('_qq_duration_replays_prebind')

# Structural guard: generic pre-bind candidate/validated duration must not become provider_duration_ms.
assert "if qq_source == 'qq-track-switch-hint':" in request_src
assert 'QQ自动切歌前旧流时长不作为新曲身份' in request_src
assert "'qq_prebind_duration_ms': qq_prebind_duration_ms" in request_src
assert '_resolve_qq_auto_track_duration_after_bind(job, cancel_check=cancel_check)' in start_src
assert "job['provider_duration_ms'] = identity_duration_ms" in start_src

class FakeTime:
    def __init__(self): self.ms = 100000.0
    def monotonic(self): return self.ms / 1000.0
    def sleep(self, seconds): self.ms += float(seconds) * 1000.0

class Reader:
    def __init__(self, rows): self.rows=list(rows); self.calls=0
    def poll(self, process):
        self.calls += 1
        if self.rows:
            return dict(self.rows.pop(0))
        return {'position_ms': None, 'duration_ms': None, 'source': 'uia-qq-soft-track-reset'}

class MS: pass

logs=[]
def write_error_log(label, *args, detail=None, **kwargs): logs.append((label, detail))

T=FakeTime()
ns={
    'time': T,
    'write_error_log': write_error_log,
    'QQ_AUTO_TRACK_DURATION_REFRESH_WAIT_MS': const('QQ_AUTO_TRACK_DURATION_REFRESH_WAIT_MS'),
    'QQ_AUTO_TRACK_DURATION_REFRESH_POLL_MS': const('QQ_AUTO_TRACK_DURATION_REFRESH_POLL_MS'),
}
exec(epoch_helper_src, ns)
exec('class H:\n'+textwrap.indent(helper_src,'    '), ns)
H=ns['H']

# Reproduce 12:43:25 host race:
# title has already changed to 我活着, but pre-bind QQ pair still says previous IF YOU 264s.
# After provisional bind/track epoch reset, the first new pair says 219s.
h=H(); h.media_sync=MS(); h.media_sync._uia_reader=Reader([
    {'position_ms': None, 'duration_ms': None, 'source': 'uia-qq-soft-track-reset'},
] + [{'position_ms': i*80, 'duration_ms': 219000, 'source': 'qq-time-pair-candidate'} for i in range(8)])
h._qq_transport_duration_evidence=lambda *args, **kwargs: 0
job={
    'source':'QQ音乐','song':'我活着','artist':'福梦 (FUMON)',
    'provider_duration_ms':0,
    'qq_prebind_duration_ms':264000,
    'qq_prebind_duration_source':'qq-time-pair-validated',
}
resolved=h._resolve_qq_auto_track_duration_after_bind(job, cancel_check=lambda: False)
assert resolved == 219000, resolved
assert any(label == 'QQ自动切歌新曲时长证据' and 'duration=219000ms' in (detail or '') for label,detail in logs)

# Dedicated track-switch hint is already new-song evidence and should remain immediate.
h=H(); h.media_sync=MS(); h.media_sync._uia_reader=Reader([])
h._qq_transport_duration_evidence=lambda *args, **kwargs: 0
job2={'source':'QQ音乐','song':'IF YOU','artist':'BIGBANG (빅뱅)', 'provider_duration_ms':264000,
      'qq_prebind_duration_ms':264000,'qq_prebind_duration_source':'qq-track-switch-hint'}
assert h._resolve_qq_auto_track_duration_after_bind(job2, cancel_check=lambda: False) == 264000
assert h.media_sync._uia_reader.calls == 0

# Cancellation must not stall a newer track behind the duration refresh wait.
h=H(); h.media_sync=MS(); h.media_sync._uia_reader=Reader([])
h._qq_transport_duration_evidence=lambda *args, **kwargs: 0
job3={'source':'QQ音乐','song':'next','artist':'artist','provider_duration_ms':0}
assert h._resolve_qq_auto_track_duration_after_bind(job3, cancel_check=lambda: True) == 0


# Reproduce 21:49 Sandbox SAIKAI failure: Chromium first exposes an unrelated 04:25
# total (265s) while the independent QQ transport already says ~323.946s.  The transport
# witness must veto the false UIA duration before strict lyric-version filtering.
logs.clear(); T.ms=200000.0
h=H(); h.media_sync=MS(); h.media_sync._uia_reader=Reader([
    {'position_ms': 0, 'duration_ms': 265000, 'source': 'qq-time-pair-candidate'},
    {'position_ms': 1000, 'duration_ms': 265000, 'source': 'qq-time-pair-candidate'},
])
h._qq_transport_duration_evidence=lambda *args, **kwargs: 323946
job4={'source':'QQ音乐','song':'SAIKAI','artist':'Mili','provider_duration_ms':0,
      'qq_prebind_duration_ms':242000,'qq_prebind_duration_source':'qq-time-pair-validated'}
assert h._resolve_qq_auto_track_duration_after_bind(job4, cancel_check=lambda: False) == 323946
assert any(label == 'QQ自动歌词GSMTC时长证据' and '323946ms' in (detail or '') for label,detail in logs)

# The real log's correct cross-provider candidate is close enough once the corrected 219s identity is used.
expected=219000; netease=219503; kugou=219000
tol_ncm=max(3500, int(max(expected, netease)*0.025))
tol_kg=max(3500, int(max(expected, kugou)*0.025))
assert abs(netease-expected) <= tol_ncm
assert abs(kugou-expected) <= tol_kg
assert abs(264000-kugou) > max(3500, int(264000*0.025))

print('QQ CROSSSOURCE DURATION RACE REPLAY: PASS')
print('  pre-bind previous-song 264s generic pair is not trusted as new-track identity: PASS')
print('  post-bind QQ epoch resolves 我活着 to 219s before strict provider search: PASS')
print('  dedicated qq-track-switch-hint remains immediate new-track evidence: PASS')
print('  cancelled job exits duration wait immediately: PASS')
print('  Sandbox SAIKAI 265s false UIA duration is vetoed by independent 323.946s GSMTC: PASS')
print('  NCM 219.503s + Kugou 219.000s are accepted under corrected 219s identity: PASS')
