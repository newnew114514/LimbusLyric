from __future__ import annotations
import sys, time
from pathlib import Path

main = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
src = main.read_text(encoding='utf-8')
start = src.index('# Release last-mile R6: recording-friendly render admission + QQ precise-duration proof')
end = src.index("try:\n    write_error_log('R2.4跨播放器可见字幕时钟安全激活'", start)
block = src[start:end]

def need(c, m):
    if not c:
        raise AssertionError(m)

for token in (
    'R6_GUI_LATE_MIN_MS = 40.0',
    "bool(row.get('duration_self_proved'))",
    "source == 'qq-time-pair-validated'",
    "ControlPanel._resolve_qq_auto_track_duration_after_bind = _r6_resolve_qq_duration",
    'LyricWindow.check_lyric_time = _r6_check_lyric_time',
    '_speculative_render_quiet_until_mono',
    'current-visible=unchanged',
):
    need(token in block, f'R6 token missing: {token}')

logs=[]
def write_error_log(*a, **kw): logs.append((a,kw))

class Reader:
    def __init__(self, row): self.row=dict(row); self.polls=0
    def poll(self, process): self.polls += 1; return dict(self.row)
class Sync:
    def __init__(self, row, key='赤と青|artist'):
        self._uia_reader=Reader(row); self._track_key=key
    def snapshot(self): return {'media_title':'赤と青','media_artist':'Artist','media_source':'QQMusic.exe'}
    def _source_matches_process_hint(self, source, process): return True
class ControlPanel:
    def __init__(self,row,key='赤と青|artist'): self.media_sync=Sync(row,key)
    def _resolve_qq_auto_track_duration_after_bind(self, job, cancel_check=None): return 0
    def _track_identity(self,song,artist): return str(song).lower()+'|'+str(artist).lower()
    def _same_track(self,a,b,c,d): return str(a).lower()==str(c).lower() and str(b).lower()==str(d).lower()
class LyricWindow:
    def __init__(self):
        self.lyric_timeline=[1]; self._last_check_mono=time.monotonic()*1000.0-120.0; self.called=0
    def check_lyric_time(self): self.called += 1; return 'legacy-return'
LyricWindow.check_lyric_time._limbus_layer='H33'
LyricWindow.check_lyric_time._limbus_qq_residency='capacity-direct-idle-preserve'

ns={
    'ControlPanel':ControlPanel,'LyricWindow':LyricWindow,'write_error_log':write_error_log,
    'time':time,
}
exec(compile(block,'<r6>','exec'),ns,ns)

# Exact regression from field log: numeric duration equals a pre-bind value, but the per-track
# QQ UIA adapter has explicitly self-proved the new advancing mm:ss stream. It must be admitted.
row={'position_ms':1000,'duration_ms':193000,'confidence':168,'source':'qq-time-pair-validated','duration_self_proved':True}
p=ControlPanel(row)
job={'source':'QQ音乐','song':'赤と青','artist':'Artist','key':'赤と青|artist','qq_prebind_duration_ms':193000}
need(p._resolve_qq_auto_track_duration_after_bind(job)==193000, 'post-bind self-proved same-value duration was not rescued')

# A merely validated row without explicit per-track advancing duration proof must remain rejected.
row2={'position_ms':1000,'duration_ms':193000,'confidence':168,'source':'qq-time-pair-validated'}
p2=ControlPanel(row2)
need(p2._resolve_qq_auto_track_duration_after_bind(job)==0, 'unproved same-value duration bypassed identity firewall')

# Track ownership mismatch must also remain rejected.
p3=ControlPanel(row, key='other|track')
need(p3._resolve_qq_auto_track_duration_after_bind(job)==0, 'self-proof crossed a bound-track mismatch')

# A real late GUI tick only silences speculative work; mature tick return and H33 metadata survive.
w=LyricWindow(); out=w.check_lyric_time()
need(out=='legacy-return' and w.called==1, 'R6 changed mature check_lyric_time return/dispatch')
need(float(getattr(w,'_speculative_render_quiet_until_mono',0.0)) > time.monotonic()*1000.0, 'late frame did not arm speculative quiet')
need(getattr(LyricWindow.check_lyric_time,'_limbus_layer','')=='H33', 'H33 public layer marker was not preserved')
need(getattr(LyricWindow.check_lyric_time,'_limbus_qq_residency','')=='capacity-direct-idle-preserve', 'H33 residency marker was not preserved')

print('RELEASE LAST-MILE R6: PASS')
print(' - QQ post-bind duration_self_proved evidence rescues exact-duration KRC selection')
print(' - unproved/prebind-only and wrong-track duration evidence remain rejected')
print(' - 40-750ms GUI late ticks quiet speculative render work without changing current/visible work')
