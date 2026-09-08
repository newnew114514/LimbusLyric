from pathlib import Path
import ast, gc, os, sys, types

if len(sys.argv) != 2:
    raise SystemExit(2)
source_path = Path(sys.argv[1])
text = source_path.read_text(encoding='utf-8')

def need(cond, msg):
    if not cond:
        print('KUGOU AUTO OVERLAY + LATE ATTACH + VISUAL DRIFT H34 REPLAY: FAIL')
        print(' - ' + msg)
        raise SystemExit(1)

markers = [
    'H34酷狗播放器切换按既有播放附着',
    'H34酷狗切歌弹幕容器已就绪',
    'H34酷狗视觉大偏差隔离',
    'H34酷狗视觉大偏差二次证明通过',
    "ControlPanel.nativeEvent._limbus_gc_guard='defer-cyclic-gc-outside-native-dispatch'",
    "MediaSessionSync._kugou_poll_visual_rail_anchor._limbus_cross_windows='large-drift-second-proof'",
]
for marker in markers:
    need(marker in text, 'missing H34 runtime marker: ' + marker)
need("panel._zero_touch_first_attach_pending=True" in text, 'player-switch late attach does not reuse startup_existing contract')
need("panel._auto_overlay_suspended=False" in text, 'new KuGou lyric result does not release stale overlay suspension before launch')
need("st['locked']=False" in text and "st['anchor']=None" in text, 'rejected visual candidate can leak H30 lease authority')
need("_py_gc.disable()" in text and "QTimer.singleShot(0" in text, 'nativeEvent GC finalizer isolation is incomplete')

# Extract H34 constants/helpers/activation without executing the application.
tree = ast.parse(text)
wanted = {
    'H34_KUGOU_VISUAL_LARGE_DRIFT_MIN_MS',
    'H34_KUGOU_VISUAL_LARGE_DRIFT_RATIO',
    'H34_KUGOU_VISUAL_SECOND_PROOF_HITS',
    'H34_KUGOU_VISUAL_SECOND_PROOF_SPAN_MS',
    'H34_KUGOU_VISUAL_SECOND_PROOF_TTL_MS',
}
nodes=[]
for node in tree.body:
    if isinstance(node, ast.Assign):
        names={t.id for t in node.targets if isinstance(t, ast.Name)}
        if names & wanted:
            nodes.append(node)
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in {
        '_h34_kugou_visual_guard_step','_h34_kugou_geometry_sane','_h34_activate_runtime'
    }:
        nodes.append(node)
ns={'os':os,'time':__import__('time'),'_py_gc':gc}
exec(compile(ast.Module(body=nodes,type_ignores=[]), str(source_path), 'exec'), ns)
need(wanted <= set(ns), 'failed to extract H34 constants')

step=ns['_h34_kugou_visual_guard_step']
sane=ns['_h34_kugou_geometry_sane']
expected=(212.0,1197.0); ey=571.0
# Field false rail: too short/narrow compared with HostV2 transport geometry.
need(not sane(expected,ey,{'x0':393,'x1':1082,'y':604}), 'field 190s false rail shape was accepted')
need(sane(expected,ey,{'x0':220,'x1':1188,'y':574}), 'plausible real KuGou rail geometry was rejected')

# Large-drift field sequence must not cross-lock: it jumps 190s -> 153s -> 64s -> 63s -> 59s.
p=None
bad=[(190432,0),(153171,1600),(64040,25500),(63821,26600),(59504,27800)]
for pos,now in bad:
    p,ok=step(p,pos,now,221000,{'x0':220,'x1':1188,'y':574})
    need(not ok, 'incoherent large-drift field sequence acquired visual authority')
# R2.2 field regression: the wrong 108s rail only moved ~0.5s while wall clock moved ~3s.
# Repetition alone must never promote that stale visual source.
p=None
for pos,now in [(108034,10000),(108210,11050),(108553,13000),(108700,14100)]:
    p,ok=step(p,pos,now,230000,{'x0':220,'x1':1188,'y':574})
    need(not ok, 'slow/stale repeated visual rail acquired authority')

# A stable same-rail sequence close to wall-clock pace still acquires, now after four proofs.
p=None; ok=False
for pos,now in [(60000,10000),(61020,11000),(62100,12150),(63210,13250)]:
    p,ok=step(p,pos,now,221000,{'x0':220,'x1':1188,'y':574})
need(ok and int(p.get('hits',0))>=4, 'coherent second visual proof did not acquire authority')

# Minimal runtime install/replay: player switch => startup-existing attach; successful new lyric => overlay container/timeline ready;
# nativeEvent => GC disabled during the native callback and restored afterwards.
class Combo:
    def __init__(self, value): self.value=value
    def currentText(self): return self.value
class Check:
    def __init__(self, value=True): self.value=value
    def isChecked(self): return self.value
class FakeMedia:
    def __init__(self):
        self._process_hint='cloudmusic.exe'; self._media_player_epoch=7
    @staticmethod
    def _process_stem(x):
        return str(x or '').lower().replace('.exe','')
    def _kugou_poll_visual_rail_anchor(self,*a,**k): return False
class FakeWindow:
    def __init__(self): self.visible=False; self.lyric_timeline=[]
    def isVisible(self): return self.visible
class FakePanel:
    def __init__(self):
        self.player_combo=Combo('酷狗音乐')
        self.source_combo=Combo('酷狗')
        self.players={'酷狗音乐':{'process':'kgmusic.exe'}}
        self.media_sync=FakeMedia()
        self._is_started=True; self._auto_armed=True; self.auto_track_check=Check(True); self.trans_check=Check(False)
        self._auto_generation=9; self._auto_target_key='song|artist'
        self._zero_touch_armed=False; self._zero_touch_player=''; self._zero_touch_first_attach_pending=False
        self._auto_overlay_suspended=True; self._auto_suspended_loaded_key='old|track'
        self._loaded_song=''; self._loaded_artist=''; self._loaded_track_key=''
        self.lyric_window=FakeWindow(); self.launches=0; self.request_seen=None
    def _warmup_selected_player(self):
        self.media_sync._process_hint='kgmusic.exe'; self.media_sync._media_player_epoch += 1; return 'warm'
    def _request_auto_track(self,song,artist=''):
        self.request_seen=(self._zero_touch_armed,self._zero_touch_player,self._zero_touch_first_attach_pending)
        return 'request'
    def _on_auto_lyric_result(self,row):
        need(self._auto_overlay_suspended is False, 'stale KuGou overlay suspension survived into legacy auto-result launch')
        self._loaded_song=row.get('song',''); self._loaded_artist=row.get('artist',''); self._loaded_track_key=row.get('key','')
        return 'result'
    def _same_track(self,a,b,c,d): return (a,b)==(c,d)
    def _launch_current_lyrics(self,start_delay=0):
        self.launches += 1; self.lyric_window.visible=True; self.lyric_window.lyric_timeline=[1]; return True
    def nativeEvent(self,eventType,message):
        need(not gc.isenabled(), 'cyclic GC was enabled inside nativeEvent')
        return ('native',0)
class FakeSyncClass:
    def _kugou_poll_visual_rail_anchor(self,*a,**k): return False
class ImmediateQTimer:
    @staticmethod
    def singleShot(ms, fn): fn()

# Installer expects actual class objects. Assign methods from fake instances/classes.
class CP:
    _warmup_selected_player=FakePanel._warmup_selected_player
    _request_auto_track=FakePanel._request_auto_track
    _on_auto_lyric_result=FakePanel._on_auto_lyric_result
    nativeEvent=FakePanel.nativeEvent
class MS:
    _kugou_poll_visual_rail_anchor=FakeSyncClass._kugou_poll_visual_rail_anchor
ns.update({
    'ControlPanel':CP,'MediaSessionSync':MS,'QTimer':ImmediateQTimer,
    'write_error_log':lambda *a,**k: None,
    '_h30_shared_visual_sample':lambda *a,**k: None,
})
ns['_h34_activate_runtime'].__globals__.update(ns)
ns['_h34_activate_runtime']()
need(getattr(CP._warmup_selected_player,'_limbus_layer','')=='H34', 'H34 warmup wrapper not installed')
need(getattr(MS._kugou_poll_visual_rail_anchor,'_limbus_layer','')=='H34', 'H34 visual wrapper not installed')
need(getattr(CP.nativeEvent,'_limbus_gc_guard','')=='defer-cyclic-gc-outside-native-dispatch', 'H34 nativeEvent guard not installed')

pnl=FakePanel()
# Call installed methods on the fake panel instance. The wrapper captures CP's original unbound methods.
need(CP._warmup_selected_player(pnl)=='warm', 'H34 warmup wrapper changed return contract')
need(getattr(pnl,'_h34_kugou_player_switch_attach_pending',False), 'QQ/NetEase -> already-playing KuGou was not marked late-attach')
need(CP._request_auto_track(pnl,'song','artist')=='request', 'H34 request wrapper changed return contract')
need(pnl.request_seen==(True,'酷狗音乐',True), 'late-attach request did not expose startup_existing flags to bind path')
need((pnl._zero_touch_armed,pnl._zero_touch_player,pnl._zero_touch_first_attach_pending)==(False,'',False), 'late-attach adapter leaked zero-touch UI state')
row={'song':'song','artist':'artist','key':'song|artist','source':'酷狗','lyric':'[00:00]x','generation':9,'trans_only':False}
need(CP._on_auto_lyric_result(pnl,row)=='result', 'H34 auto-result wrapper changed return contract')
need(pnl.launches==1 and pnl.lyric_window.visible and pnl.lyric_window.lyric_timeline, 'successful KuGou track did not automatically restore visible/running overlay')
need(pnl._auto_overlay_suspended is False, 'KuGou new track ended with overlay suspended')

was=gc.isenabled()
if not was: gc.enable()
need(CP.nativeEvent(pnl,1,2)==('native',0), 'H34 nativeEvent wrapper changed return contract')
need(gc.isenabled(), 'cyclic GC was not restored after nativeEvent')
if not was: gc.disable()

print('KUGOU AUTO OVERLAY + LATE ATTACH + VISUAL DRIFT H34 REPLAY: PASS')
print(' - running-session player switch to KuGou reuses startup_existing attach and forbids synthetic zero')
print(' - successful KuGou auto lyrics restore the session overlay container/timeline intent without another Start click')
print(' - 190s/153s/64s field false rails cannot cross-lock over a ~12s current clock')
print(' - a stable same-geometry physical rail can pass the independent second proof')
print(' - cyclic GC/comtypes finalization is deferred out of the input-synchronous nativeEvent callback')
