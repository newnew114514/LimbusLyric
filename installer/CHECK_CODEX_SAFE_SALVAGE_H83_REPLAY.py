"""H83 safe Codex salvage: NetEase lifecycle + row-material style ownership."""
import ast, asyncio, importlib.util, sys, threading, time
from pathlib import Path
from types import ModuleType, SimpleNamespace as NS
from collections import OrderedDict
sys.dont_write_bytecode=True
root=Path(sys.argv[1]); main=next(root.glob('LimbusLyric_*.py'))
tree=ast.parse(main.read_text(encoding='utf-8')); top={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
checks=[]
def ck(name,v): checks.append(bool(v)); print(('PASS ' if v else 'FAIL ')+name,flush=True)
def load(names,ns): exec(compile(ast.Module(body=[top[n] for n in names],type_ignores=[]),str(main),'exec'),ns)
# NetEase native lifecycle
stub=ModuleType('cloudmusic_detector'); stub.AsyncCloudMusic=None; sys.modules['cloudmusic_detector']=stub
spec=importlib.util.spec_from_file_location('_h83_native',root/'limbus_netease_native.py'); native=importlib.util.module_from_spec(spec); spec.loader.exec_module(native)
async def lifecycle():
 class Broken:
  def __init__(self): raise OSError('injected')
 native.AsyncCloudMusic=Broken; a=native.NeteaseNativeClockAdapter(); a.start_background(); escaped=None
 try: await a._start_task
 except Exception as e: escaped=type(e).__name__
 ck('native constructor error becomes backoff state',escaped is None and a._start_state=='error' and a._retry_after_mono>time.monotonic())
 started,cleaning,finish=asyncio.Event(),asyncio.Event(),asyncio.Event(); instances=[]
 class Detector:
  def __init__(self): self.number=len(instances); self.stopped=False; instances.append(self)
  async def start(self):
   if self.number==0: started.set(); await asyncio.Event().wait()
  async def stop(self):
   if self.number==0: cleaning.set(); await finish.wait()
   self.stopped=True
 native.AsyncCloudMusic=Detector; a=native.NeteaseNativeClockAdapter(); a.start_background(); old=a._start_task; await started.wait(); a.stop_background(); await cleaning.wait()
 for _ in range(4): a.stop_background()
 ck('restart waits for cancellation cleanup',not a.start_background() and len(instances)==1)
 ck('repeated stop cancels startup only once',old.cancelling()==1)
 finish.set()
 try: await old
 except asyncio.CancelledError: pass
 a.start_background(); await a._start_task; ck('restart recovers after cleanup',a._cm is instances[-1] and a._start_state=='ready')
 await a.stop_async(); ck('full stop releases detector and loop',a._cm is None and a._loop is None and all(x.stopped for x in instances))
# Row-material style ownership

def material():
 ns=dict(OrderedDict=OrderedDict,_fragment_style_signature=lambda font,*a:font,_h69_install_pre=lambda w,p:None,
         _h62_queue_decay_build=lambda row:None,write_error_log=lambda *a,**kw:None)
 load(['_h61_row_key','_h61_held_row_key','_h61_row_cache_init','_h61_cache_row_shared','_h69_install_song_fragment_atlas'],ns)
 row=NS(text='same lyric',font='new style',color=None,stroke_color=None,stroke_width=0,outline_enabled=False,shadow_enabled=False,shadow_color=None,glow=False,glow_color=None,glow_size=0,glow_alpha=0,_shared_fragment_atlas=None)
 w=NS(full_text='',history_lines=[row],fading_lines=[],update=lambda:None,_current_fragment_style_signature=lambda:'new style')
 ns['H61_ROW_CACHE_MAX_ENTRIES']=12; ns['H61_ROW_CACHE_MAX_PIXELS']=18*1024*1024
 old=('old sheet',{},'old style',100); new=('new sheet',{},'new style',100)
 for sh in (old,new): ns['_h61_cache_row_shared'](w,(sh[2],row.text),sh); ns['_h69_install_song_fragment_atlas'](w,dict(h61_row_fallback=True,row_key=(sh[2],row.text),style_sig=sh[2],text=row.text))
 ck('late row material cannot cross style identity',row._shared_fragment_atlas is new)
 row.font='old style'; row._shared_fragment_atlas=None
 ns['_h69_install_song_fragment_atlas'](w,dict(h61_row_fallback=True,row_key=('old style',row.text),style_sig='old style',text=row.text))
 ck('historical row still receives its own old style',row._shared_fragment_atlas is old)
asyncio.run(lifecycle()); material(); print(f'H83 CODEX SAFE SALVAGE: {sum(checks)}/{len(checks)} PASS'); raise SystemExit(0 if all(checks) else 1)
