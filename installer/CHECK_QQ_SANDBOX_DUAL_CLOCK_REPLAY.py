from pathlib import Path
import ast, sys, textwrap, threading

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_QQ_SANDBOX_DUAL_CLOCK_REPLAY.py <main.py>')
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8')
tree=ast.parse(source)

def method_source(cls_name, method):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name==cls_name:
            for item in node.body:
                if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)) and item.name==method:
                    return ast.get_source_segment(source,item)
    raise AssertionError(f'missing {cls_name}.{method}')

def const(name, default=None):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            return ast.literal_eval(node.value)
    if default is not None: return default
    raise AssertionError(f'missing const {name}')

class FakeTime:
    def __init__(self): self.mono=100000.0; self.wall=1786850600000.0
    def monotonic(self): return self.mono/1000.0
    def time(self): return self.wall/1000.0
    def step(self,ms): self.mono+=ms; self.wall+=ms
T=FakeTime()
logs=[]
def write_error_log(label, *args, detail=None, **kwargs): logs.append((label,detail))

ns={'time':T,'write_error_log':write_error_log}
for name in [
 'QQ_DIRECT_GSMTC_FRESH_TIMESTAMP_MS','QQ_DIRECT_GSMTC_SEEK_REANCHOR_MIN_DELTA_MS',
 'QQ_DIRECT_GSMTC_SEEK_AUTHORITY_MS','QQ_GSMTC_IDENTITY_GUARD_ENABLED',
 'QQ_GSMTC_IDENTITY_DURATION_TOLERANCE_MIN_MS','QQ_GSMTC_IDENTITY_DURATION_TOLERANCE_RATIO',
 'QQ_GSMTC_IDENTITY_SEEK_CONFIRM_MAX_GAP_MS','QQ_DIRECT_GSMTC_POSITION_VETO_MIN_DELTA_MS'
]: ns[name]=const(name)
methods=['_qq_direct_gsmtc_witness','_qq_update_gsmtc_identity_guard','_qq_apply_direct_gsmtc_seek_authority','_qq_direct_public_clock_override']
body='\n\n'.join(textwrap.indent(method_source('MediaSessionSync',m),'    ') for m in methods)
exec('class SyncHarness:\n'+body,ns)
Sync=ns['SyncHarness']

def make_sync():
    s=Sync(); s._track_key='少女a|x'; s._uia_duration_ms=221000
    s._qq_gsmtc_identity_guard_active=False; s._qq_gsmtc_identity_duration_ms=None
    s._qq_gsmtc_identity_last_position_ms=None; s._qq_gsmtc_identity_last_mono=None
    s._qq_gsmtc_identity_seek_pending=None; s._qq_gsmtc_identity_last_diag_mono=0.0
    s._qq_gsmtc_last_position_ms=None; s._qq_gsmtc_last_mono=None; s._qq_gsmtc_good_streak=0; s._qq_gsmtc_primary=False
    s._qq_gsmtc_identity_seek_confirmed_mono=0.0; s._qq_gsmtc_identity_seek_confirmed_position_ms=None
    s._qq_direct_gsmtc_state=None; s._qq_direct_gsmtc_authority_until_mono=0.0
    s._uia_position_ms=None; s._uia_anchor_mono=None; s._uia_observed_ms=None; s._uia_status='unknown'; s._uia_has_lock=False; s._uia_last_seen_mono=None
    s._qq_seek_pending=None; s._playing_seek_pending=None; s._paused_seek_pending=None; s._uia_pending_far=None; s._qq_unarmed_far_pending=None
    s._qq_gesture_recent_until_mono=0.0; s._qq_gesture_expected_ms=None; s._qq_gesture_expected_id=0; s._qq_mouse_is_down=False
    s._qq_last_rail_commit_mono=0.0; s._qq_last_rail_commit_target=None; s._qq_seek_last_commit_mono=0.0; s._qq_seek_last_commit_target=None
    s._qq_reset_clock_authority=lambda preserve_phase_baseline=False: None
    return s

# A. Sandbox startup: paused source-affine raw 3994 must stay independent of UIA 79s.
s=make_sync(); last=T.wall-2_000_000
pos,tr=s._qq_direct_gsmtc_witness(3994,last,'paused',221626,1.0)
assert tr and 3900<=pos<=4100,(pos,tr)
assert s._qq_update_gsmtc_identity_guard(pos,tr,'paused',221626)

# Execute the real async UIA guard method against a 79s validated UIA sample.
async_methods=['set_qq_gsmtc_identity_guard','_guard_qq_duration_mismatch_result']
body2='\n\n'.join(textwrap.indent(method_source('AsyncPlayerUiPositionReader',m),'    ') for m in async_methods)
ns2=dict(ns); ns2['threading']=threading; ns2['QQ_GSMTC_IDENTITY_UIA_REACQUIRE_COOLDOWN_MS']=const('QQ_GSMTC_IDENTITY_UIA_REACQUIRE_COOLDOWN_MS')
exec('class AsyncHarness:\n'+body2,ns2); A=ns2['AsyncHarness'](); A._lock=threading.Lock(); A._qq_gsmtc_identity_guard={}; A._qq_gsmtc_guard_last_reacquire_mono=0.0; A._qq_gsmtc_guard_last_diag_mono=0.0
A.set_qq_gsmtc_identity_guard(True,221000,221626,pos,position_veto=True)
r=A._guard_qq_duration_mismatch_result(None,'qqmusic.exe',{'position_ms':79000,'duration_ms':221000,'confidence':168,'source':'qq-time-pair-validated'})
assert r['position_ms'] is None and r['source']=='qq-gsmtc-veto-uia-position',r

# B. Stale ~119s gesture versus real raw GSMTC jump 10s -> 30s. Two raw samples must cancel it.
s=make_sync(); s._uia_position_ms=12000.0; s._uia_anchor_mono=T.mono; s._uia_status='playing'; s._qq_gesture_expected_ms=118685.0; s._qq_gesture_expected_id=4; s._qq_gesture_recent_until_mono=T.mono+6000; s._qq_seek_pending={'gesture_id':4}
for raw in (10000,10200):
    p0,t0=s._qq_direct_gsmtc_witness(raw,T.wall-40,'playing',221626,1.0); s._qq_update_gsmtc_identity_guard(p0,t0,'playing',221626); T.step(200)
p1,t1=s._qq_direct_gsmtc_witness(30286,T.wall-40,'playing',221626,1.0); s._qq_update_gsmtc_identity_guard(p1,t1,'playing',221626); T.step(203)
p2,t2=s._qq_direct_gsmtc_witness(30706,T.wall-20,'playing',221626,1.0); s._qq_update_gsmtc_identity_guard(p2,t2,'playing',221626)
assert getattr(s,'_qq_gsmtc_identity_seek_confirmed_position_ms',None) is not None
assert s._qq_apply_direct_gsmtc_seek_authority(p2,'playing')
assert s._qq_gesture_expected_ms is None and s._qq_seek_pending is None
assert 29000 <= s._uia_position_ms <= 32000, s._uia_position_ms

# C. Recent rail commit cannot quarantine a genuine restart proven by direct raw 1.2->1.5s.
T.step(1000); s=make_sync(); s._uia_position_ms=43000.0; s._uia_anchor_mono=T.mono; s._uia_status='playing'; s._qq_last_rail_commit_mono=T.mono-1800; s._qq_last_rail_commit_target=41827.0
p,t=s._qq_direct_gsmtc_witness(41000,T.wall-20,'playing',221626,1.0); s._qq_update_gsmtc_identity_guard(p,t,'playing',221626); T.step(200)
p,t=s._qq_direct_gsmtc_witness(41200,T.wall-20,'playing',221626,1.0); s._qq_update_gsmtc_identity_guard(p,t,'playing',221626); T.step(200)
p,t=s._qq_direct_gsmtc_witness(1200,T.wall-10,'playing',221626,1.0); s._qq_update_gsmtc_identity_guard(p,t,'playing',221626); T.step(203)
p,t=s._qq_direct_gsmtc_witness(1420,T.wall-10,'playing',221626,1.0); s._qq_update_gsmtc_identity_guard(p,t,'playing',221626)
assert s._qq_apply_direct_gsmtc_seek_authority(p,'playing')
assert s._qq_last_rail_commit_mono==0.0 and s._qq_last_rail_commit_target is None
assert 1000<=s._uia_position_ms<=2000,s._uia_position_ms

# D. Host raw/default timestamp: direct lane must be absent.
s=make_sync(); p,t=s._qq_direct_gsmtc_witness(0,-11644473600000,'playing',221626,1.0)
assert p is None and not t,(p,t)

# E. Execute real LyricSearchEngine.search with provider stubs: QQ failure -> NCM 264215 succeeds; 148s stays rejected.
search_src=method_source('LyricSearchEngine','search')
class MetaBase:
    last_error=''; meta={}
    @classmethod
    def _set_provider_meta(cls,**kw): cls.meta=dict(kw)
    @classmethod
    def last_provider_meta(cls): return dict(cls.meta)
    @classmethod
    def _is_cancelled(cls): return False
    @staticmethod
    def _clean_lrc(x,*a): return x or ''
    @staticmethod
    def _merge_intro_credits(a,b): return a or ''
ns3={'write_error_log':write_error_log,'_translation_to_line_lrc':lambda t,l:t or '', '_extract_native_chinese_lrc':lambda x:'', '_merge_translation_native_chinese':lambda t,l:t, '_lyric_clock_quality':lambda x: (3 if '<00:' in str(x or '') else (1 if '[00:' in str(x or '') else 0)), '_provider_payload_instrumental':lambda source,text,duration_ms=0,provider_meta=None:False, '_build_lyric_payload_meta':lambda base,source,text,duration_ms=0,provider_meta=None:dict(base or {},lyric_payload_source=source,lyric_payload_instrumental=False), '_verify_precise_enhancement_against_native':lambda ref,cand,**kw:(cand,{'matches':4,'coverage':1.0},'fixture'), 'MetaBase':MetaBase}
exec('class SearchHarness(MetaBase):\n'+textwrap.indent(search_src,'    '),ns3)
Search=ns3['SearchHarness']
ns3['LyricSearchEngine']=Search
Search.search_qq=staticmethod(lambda *a,**k:(None,None,0))
Search.search_netease=staticmethod(lambda *a,**k:('[00:00.00]IF YOU',None,264215))
Search.search_kugou=staticmethod(lambda *a,**k:('[00:00.00]wrong',None,148000))
lyr,dur=Search.search('IF YOU','BIGBANG (빅뱅)','QQ音乐',False,None,264000)
assert lyr and 'IF YOU' in lyr and 263000<=dur<=265000,(lyr,dur)
assert Search.meta.get('source')=='QQ音乐' and Search.meta.get('lyric_payload_source')=='网易云',Search.meta

# Wrong-only candidate must fail closed.
Search.search_netease=staticmethod(lambda *a,**k:('[00:00.00]wrong',None,148000))
Search.search_kugou=staticmethod(lambda *a,**k:(None,None,0))
lyr,dur=Search.search('IF YOU','BIGBANG (빅뱅)','QQ音乐',False,None,264000)
assert lyr is None,(lyr,dur)

print('QQ SANDBOX DUAL-CLOCK + CROSS-SOURCE REPLAY: PASS')
print('  startup raw GSMTC 4s vetoes contradictory UIA 79s: PASS')
print('  stale 119s gesture terminated by independent raw 30s seek proof: PASS')
print('  recent-rail stale guard released by genuine 43s->1s restart: PASS')
print('  host invalid GSMTC lane remains dormant: PASS')
print('  QQ 264s full-lyric miss safely borrows NCM 264.2s; 148s rejected: PASS')
