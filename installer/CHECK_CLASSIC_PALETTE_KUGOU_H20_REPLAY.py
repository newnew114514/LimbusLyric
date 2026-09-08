from pathlib import Path
import ast, sys, threading, time, re

ROOT=Path(__file__).resolve().parents[1]
main=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
source=main.read_text(encoding='utf-8')
assert 'CLASSIC EXIT + PALETTE + KUGOU PRESENTATION + PACKAGING H20' in source
assert source.index('# H20 classic-exit / palette / KuGou presentation / packaging closure') < source.index('# H14 auto-precision deadline / bounded enhancement')
for token in [
    "('整行淡出（经典）','fade')",
    "('逐字消失（经典）','per_char')",
    "('从左到右消失（经典）','wipe_ltr')",
    "('从右到左消失（经典）','wipe_rtl')",
    "('快速收缩/淡出（经典）','shrink')",
    "('柔和下沉淡出','soft_drift')",
    '_LIMBUS_H20_FADING_UPDATE_CLASSIC',
    '_LIMBUS_H20_FADING_DRAW_CLASSIC',
    'H20酷狗HostV2时长证据复用',
    'H20酷狗空白段保留清晰历史',
    'H20重复手动抓词合并精准任务',
    'H20同曲手动快速歌词免重启',
    "if not style.get('glow_color'):",
]:
    assert token in source, token

# Pure palette scorer: a huge neutral field must not drown a smaller blue accent.
tree=ast.parse(source)
want={'_h20_cover_accent_from_rgb_rows','_h20_kugou_ui_duration_hint'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in want]
assert {n.name for n in nodes}==want
palette_node=next(n for n in nodes if n.name=='_h20_cover_accent_from_rgb_rows')
mod=ast.Module(body=[palette_node],type_ignores=[]); ast.fix_missing_locations(mod)
ns={}
exec(compile(mod,str(main),'exec'),ns)
rgb=ns['_h20_cover_accent_from_rgb_rows']([(48,132,190,180),(190,90,70,70)],total_valid=1200)
assert rgb and rgb[2] > rgb[0] and rgb[2] > rgb[1], rgb
assert max(rgb) >= 190, rgb
# Nearly monochrome art with only a tiny tinted artifact must remain neutral.
assert ns['_h20_cover_accent_from_rgb_rows']([(48,132,190,35)],total_valid=1200) is None

# Fresh Host-V2 duration evidence must bypass the slow legacy MSAA probe.
hint_node=next(n for n in nodes if n.name=='_h20_kugou_ui_duration_hint')
mod2=ast.Module(body=[hint_node],type_ignores=[]); ast.fix_missing_locations(mod2)
class Lock:
    def __enter__(self): return self
    def __exit__(self,*a): return False
slow=[]
def old(*a,**k): slow.append(1); return 99999
ns2={
    '_clean_name':lambda x: re.sub(r'\W+','',str(x).casefold()),
    '_LIMBUS_H20_KUGOU_DURATION_LOCK':Lock(),
    '_LIMBUS_H20_KUGOU_DURATION_HINTS':{'少女a':(221000,time.monotonic())},
    'H20_KUGOU_DURATION_HINT_TTL_SEC':8.0,
    '_LIMBUS_H20_KUGOU_UI_HINT_PRE':old,
    'time':time,
    'write_error_log':lambda *a,**k:None,
}
exec(compile(mod2,str(main),'exec'),ns2)
assert ns2['_h20_kugou_ui_duration_hint']([1],'少女A')==221000
assert not slow, 'fresh Host-V2 evidence should not call legacy MSAA duration probe'



# Same-track manual fast results must not restart the renderer when current lyrics are equal
# or better. This is the real-machine regression behind visual_count dropping to 0/1 after
# repeated manual clicks while a precise KuGou upgrade was already in flight.
manual_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h20_manual_apply')
mod3=ast.Module(body=[manual_node],type_ignores=[]); ast.fix_missing_locations(mod3)
manual_old=[]
class TextInput:
    def toPlainText(self): return '[00:01.00]old precise'
class Status:
    def setText(self,x): self.value=x
class ManualSelf:
    _is_started=True; _loaded_song='少女A'; _loaded_artist='鏡音リン、椎名もた'
    text_input=TextInput(); status=Status()
    def _same_track(self,a,b,c,d): return a.casefold()==c.casefold()
ns3={
    '_lyric_clock_quality':lambda text: 3 if 'precise' in str(text) else 1,
    '_LIMBUS_H20_MANUAL_APPLY_PRE':lambda self,result: manual_old.append(result) or False,
    'write_error_log':lambda *a,**k:None,
}
exec(compile(mod3,str(main),'exec'),ns3)
assert ns3['_h20_manual_apply'](ManualSelf(),{'stage':'fast','lyric':'[00:01.00]ordinary','song':'少女A','artist':'鏡音リン、椎名もた'}) is True
assert not manual_old, 'same-track fast result must not restart the renderer'

# A second manual click while the same-track precision request is pending must coalesce
# instead of starting another fast/precise transaction.
fetch_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h20_manual_fetch')
mod4=ast.Module(body=[fetch_node],type_ignores=[]); ast.fix_missing_locations(mod4)
fetch_old=[]
class Combo:
    def currentText(self): return '酷狗'
class FetchSelf:
    _loaded_song='少女A'; _loaded_artist='鏡音リン、椎名もた'; source_combo=Combo(); status=Status()
    _h20_manual_precise_pending=(7,'少女a|鏡音リン、椎名もた','酷狗',time.monotonic())
    def _track_identity(self,a,b): return f'{a.casefold()}|{b}'
ns4={
    'time':time,'H20_MANUAL_PRECISE_PENDING_MAX_SEC':20.0,
    '_LIMBUS_H20_MANUAL_FETCH_PRE':lambda self: fetch_old.append(1) or True,
    'write_error_log':lambda *a,**k:None,
}
exec(compile(mod4,str(main),'exec'),ns4)
assert ns4['_h20_manual_fetch'](FetchSelf()) is False
assert not fetch_old, 'duplicate manual click must be coalesced'

# KuGou long-gap cleanup may fade the current completed row, but must preserve the configured
# clear history tail instead of deleting every readable previous line.
idle_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h20_provider_idle_release')
mod5=ast.Module(body=[idle_node],type_ignores=[]); ast.fix_missing_locations(mod5)
class IdleSelf:
    _last_sync_source='kugou'; max_visible_subtitles=3; history_lines=['h0','h1','h2']
    def _enforce_visual_stack_limit(self): return 0
    def update(self): pass
idle_calls=[]
def idle_old(self,*a,**k):
    idle_calls.append(list(self.history_lines))
    self.history_lines=[]
    return True
ns5={'_LIMBUS_H20_PROVIDER_IDLE_PRE':idle_old,'write_error_log':lambda *a,**k:None}
exec(compile(mod5,str(main),'exec'),ns5)
fake=IdleSelf()
assert ns5['_h20_provider_idle_release'](fake,2,20000,(12000,5000,23000)) is True
assert idle_calls==[[]], idle_calls
assert fake.history_lines==['h1','h2'], fake.history_lines

# H20 must not alter timing/seek authority in its block.
h20=source[source.index('# H20 classic-exit / palette / KuGou presentation / packaging closure'):source.index('# H14 auto-precision deadline / bounded enhancement')]
for forbidden in ['bind_track(', 'seek_serial', '_commit_seek', '_kugou_seed_rail_local_master(']:
    assert forbidden not in h20, forbidden
print('CLASSIC EXIT + PALETTE + KUGOU PRESENTATION H20 REPLAY: PASS')
