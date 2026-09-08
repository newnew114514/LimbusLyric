from pathlib import Path
import ast, sys, time

if len(sys.argv) != 2:
    raise SystemExit(2)
text=Path(sys.argv[1]).read_text(encoding='utf-8')

def need(c,m):
    if not c:
        print('AUTO RESULT OWNERSHIP H50 REPLAY: FAIL')
        print(' - '+m)
        raise SystemExit(1)

for marker in ('AUTO RESULT OWNERSHIP H50','H50过期自动歌词结果不得清除当前任务','obsolete-final-cannot-clear-current-inflight'):
    need(marker in text,'missing H50 marker: '+marker)

tree=ast.parse(text)
fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h50_activate_runtime'),None)
need(fn is not None,'H50 activation missing')

class Combo:
    def __init__(self,v): self.v=v
    def currentText(self): return self.v
class Toggle:
    def __init__(self,v=True): self.v=v
    def isChecked(self): return self.v
class Panel:
    def __init__(self):
        self._auto_generation=8; self._auto_target_key='c|artist'; self._auto_fetch_in_progress=True
        self._is_started=True; self._auto_armed=True
        self.auto_track_check=Toggle(True); self.trans_check=Toggle(False)
        self.source_combo=Combo('网易云')

# Install the actual H50 wrapper around a minimal historical handler that reproduces the
# legacy unconditional final-result clear.
class CP:
    def _on_auto_lyric_result(self,row):
        if not bool(row.get('precision_upgrade_pending')):
            self._auto_fetch_in_progress=False
        # A current H49-style rejected transaction is allowed to close itself.
        if row.get('simulate_current_close'):
            self._auto_target_key=''; self._auto_fetch_in_progress=False
        return 'ok'

logs=[]
runtime={'ControlPanel':CP,'SOURCE_GUARD_ENABLED':True,'write_error_log':lambda *a,**k: logs.append((a,k))}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(sys.argv[1]),'exec'),runtime)
runtime['_h50_activate_runtime']()

p=Panel(); p.__class__=type('P',(Panel,CP),{})
# Re-initialize method resolution by calling wrapper borrowed from CP.
p._on_auto_lyric_result=runtime['ControlPanel']._on_auto_lyric_result.__get__(p,p.__class__)
stale={'generation':7,'key':'b|artist','source':'网易云','trans_only':False,'precision_upgrade_pending':False,'cancelled':True}
p._on_auto_lyric_result(stale)
need(p._auto_fetch_in_progress is True,'obsolete final cleared the newer current in-flight witness')
need(p._auto_target_key=='c|artist' and p._auto_generation==8,'obsolete final changed newer transaction identity')

# Current final result must close normally and must never be restored by H50.
p2=Panel(); p2._auto_target_key='c|artist'
p2.__class__=p.__class__; p2._on_auto_lyric_result=runtime['ControlPanel']._on_auto_lyric_result.__get__(p2,p2.__class__)
current={'generation':8,'key':'c|artist','source':'网易云','trans_only':False,'precision_upgrade_pending':False}
p2._on_auto_lyric_result(current)
need(p2._auto_fetch_in_progress is False,'current final result was incorrectly kept in-flight')

# A current rejection/cleanup that changes target inside the historical stack must stay closed.
p3=Panel(); p3.__class__=p.__class__; p3._on_auto_lyric_result=runtime['ControlPanel']._on_auto_lyric_result.__get__(p3,p3.__class__)
current_close=dict(current,simulate_current_close=True)
p3._on_auto_lyric_result(current_close)
need(p3._auto_fetch_in_progress is False and p3._auto_target_key=='','current cleanup was resurrected')

# Stop/invalidation during an obsolete callback changes generation/target; restoration is forbidden.
class CPInvalidate:
    def _on_auto_lyric_result(self,row):
        self._auto_fetch_in_progress=False; self._auto_generation+=1; self._auto_target_key=''; return 'ok'
runtime2={'ControlPanel':CPInvalidate,'SOURCE_GUARD_ENABLED':True,'write_error_log':lambda *a,**k:None}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(sys.argv[1]),'exec'),runtime2); runtime2['_h50_activate_runtime']()
p4=Panel(); p4.__class__=type('P4',(Panel,CPInvalidate),{}); p4._on_auto_lyric_result=runtime2['ControlPanel']._on_auto_lyric_result.__get__(p4,p4.__class__)
p4._on_auto_lyric_result(stale)
need(p4._auto_fetch_in_progress is False and p4._auto_target_key=='' and p4._auto_generation==9,'invalidated transaction was resurrected')

print('AUTO RESULT OWNERSHIP H50 REPLAY: PASS')
print(' - obsolete final callbacks cannot clear a newer overlapping auto job')
print(' - current final/cleanup and stop invalidation remain authoritative')
