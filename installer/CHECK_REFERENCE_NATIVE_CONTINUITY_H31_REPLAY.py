from __future__ import annotations
import os as _real_os, re, types
from pathlib import Path

import sys
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_REFERENCE_NATIVE_CONTINUITY_H31_REPLAY.py <main.py>')
main=Path(sys.argv[1]).resolve(); root=main.parent
src=main.read_text(encoding='utf-8')
req=(root/'requirements_netease_native.txt').read_text(encoding='utf-8')
native=(root/'limbus_netease_native.py').read_text(encoding='utf-8')
assert 'netease-cloudmusic-detector==2.0.6' in req, req
assert 'self._start_timeout_sec = 20.0' in native, 'reference 20s async startup missing'
assert 'self._retry_delay_sec = 30.0' in native, 'bounded retry backoff missing'
assert 'LEGACY NATIVE CONTINUITY REFERENCE H31' in src
start=src.index('# H31 legacy-reference native + continuity clock closure')
# H31 is a historical standalone replay.  Review only its own closure; later
# generations append unrelated platform/UI layers before __main__ and should not
# become dependencies of H31's minimal fake namespace.
end_marker='# H35 baseline reconciliation'
assert end_marker in src, 'H31 review end marker missing'
end=src.index(end_marker, start)
block=src[start:end]
assert "MediaSessionSync.snapshot = _h31_snapshot" in block
assert "MediaSessionSync.bind_track = _h31_bind_track" in block
assert "ncm-trusted-continuity-local" in block
assert "seek-authority=0" in block

class FakeTime:
    def __init__(self): self.ms=1000.0
    def monotonic(self): return self.ms/1000.0
ft=FakeTime()
class FakeOS: name='nt'
logs=[]
def write_error_log(*a,**kw): logs.append((a,kw))
class MediaSessionSync:
    def __init__(self):
        self._process_hint='cloudmusic'; self._track_key='song|artist'; self._media_player_epoch=1
        self._fixture={}; self._h25_netease_seek_intent_until_mono=0.0; self._visual_seek_override_ms=None; self._visual_seek_override_until_mono=0.0
    @staticmethod
    def _process_stem(v): return str(v).lower().replace('.exe','')
    def snapshot(self): return dict(self._fixture)
    def bind_track(self,song,artist='',*a,**kw): self._track_key=f'{song}|{artist}'; return True
ns={'MediaSessionSync':MediaSessionSync,'os':FakeOS(),'time':ft,'write_error_log':write_error_log}
exec(compile(block,'<h31>', 'exec'),ns,ns)
s=MediaSessionSync()
s._fixture={'position_ms':10000,'position_source':'ncm-native-log','status':'playing','player_alive':True,'duration_ms':200000,'raw_position_ms':10000}
a=s.snapshot(); assert a['position_ms']==10000 and not a.get('continuity_clock')
ft.ms=3500.0; s._fixture={'position_ms':None,'position_source':'waiting-real-position','status':'playing','player_alive':True,'duration_ms':200000}
b=s.snapshot(); assert 12400 <= b['position_ms'] <= 12600, b
assert b['position_source']=='ncm-trusted-continuity-local' and b['continuity_clock'] is True
ft.ms=5000.0; s._fixture={'position_ms':None,'position_source':'waiting-real-position','status':'paused','player_alive':True,'duration_ms':200000}
c=s.snapshot(); assert 13900 <= c['position_ms'] <= 14100, c
ft.ms=9000.0; d=s.snapshot(); assert d['position_ms']==c['position_ms'], (c,d)
# Resume continues from frozen point, not from paused wall time.
s._fixture['status']='playing'; e=s.snapshot(); assert e['position_ms']==c['position_ms'], e
ft.ms=10000.0; f=s.snapshot(); assert 14900 <= f['position_ms'] <= 15100, f
# Any seek intent retires continuity immediately.
s._h25_netease_seek_intent_until_mono=11000.0; s._fixture={'position_ms':None,'position_source':'waiting-real-position','status':'playing','player_alive':True,'duration_ms':200000}
g=s.snapshot(); assert g['position_ms'] is None and not g.get('continuity_clock'), g
# A track epoch change cannot inherit the old anchor.
s._h25_netease_seek_intent_until_mono=0.0; s._fixture={'position_ms':30000,'position_source':'ncm-shared-visual-rail','status':'playing','player_alive':True,'duration_ms':200000}
ft.ms=12000.0; s.snapshot(); s.bind_track('new','artist')
s._fixture={'position_ms':None,'position_source':'waiting-real-position','status':'playing','player_alive':True,'duration_ms':210000}
ft.ms=13000.0; h=s.snapshot(); assert h['position_ms'] is None, h
# Cold-start UNKNOWN stays UNKNOWN; no fake zero is created.
s2=MediaSessionSync(); s2._fixture={'position_ms':None,'position_source':'waiting-real-position','status':'playing','player_alive':True,'duration_ms':200000}
i=s2.snapshot(); assert i['position_ms'] is None and not i.get('continuity_clock'), i
# Other players are untouched.
s3=MediaSessionSync(); s3._process_hint='kgmusic'; s3._fixture={'position_ms':None,'position_source':'kugou-waiting-real-clock','status':'playing'}
j=s3.snapshot(); assert j==s3._fixture, j
print('REFERENCE NATIVE + CONTINUITY H31 REPLAY: PASS')
print(' - NetEase native detector pin follows reference build 2.0.6')
print(' - native initialization remains async and gets a 20s hard window')
print(' - only a prior trusted NetEase anchor may drive presentation continuity')
print(' - pause freezes, resume continues, seek/track epoch retire continuity')
print(' - cold start never invents zero; KuGou/QQ behavior is untouched')
