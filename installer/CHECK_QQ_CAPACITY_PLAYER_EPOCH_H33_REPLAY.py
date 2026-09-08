from __future__ import annotations
import sys, types
from pathlib import Path
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_QQ_CAPACITY_PLAYER_EPOCH_H33_REPLAY.py <main.py>')
main=Path(sys.argv[1]).resolve(); src=main.read_text(encoding='utf-8')
assert 'QQ CAPACITY EPOCH CLOSURE H33' in src
start=src.index('# H33 QQ capacity + player-epoch transport-hint closure')
end=src.index('# H31 legacy-reference native + continuity clock closure',start)
block=src[start:end]
for token in (
    "LyricWindow.check_lyric_time=_h33_check_lyric_time",
    "ControlPanel._note_auto_transport_hint=_h33_note_hint",
    "ControlPanel._auto_transport_hint_active=_h33_hint_active",
    "residency=capacity",
    "identity-authority=reject",
):
    assert token in block, token
# H33 is presentation/identity ownership only; it must not install transport clock methods.
for forbidden in ('MediaSessionSync.snapshot=', 'MediaSessionSync.bind_track=', '_kugou_commit_gesture_seek=', 'position_ms=0'):
    assert forbidden not in block, forbidden

logs=[]
def write_error_log(*a,**kw): logs.append((a,kw))
class Combo:
    def __init__(self,name): self.name=name
    def currentText(self): return self.name
class MS: _media_player_epoch=1
class ControlPanel:
    def __init__(self):
        self.player_combo=Combo('QQ音乐'); self.media_sync=MS(); self._auto_transport_hint_until=0.0; self._auto_transport_hint_source=''
    def _note_auto_transport_hint(self,source,ttl=2.8):
        self._auto_transport_hint_until=100.0; self._auto_transport_hint_source=str(source); return None
    def _auto_transport_hint_active(self): return bool(self._auto_transport_hint_until>0.0)
class LyricWindow:
    def __init__(self,qq=True):
        self._last_sync_source='QQMusic.exe' if qq else 'cloudmusic'; self._last_sync_position_source='qq-gsmtc' if qq else 'ncm-native-log'
        self.max_visible_subtitles=3; self.history_lines=['h1','h2']; self.full_text='current'; self._provider_idle_suppressed_line=-1; self.updated=0
    def check_lyric_time(self):
        # Replay the historical direct-idle landing branch: it suppresses current row and
        # clears all held history before returning.
        self.history_lines=[]; self.full_text=''; self._provider_idle_suppressed_line=7; return 'legacy-return'
    def _enforce_visual_stack_limit(self):
        keep=max(0,self.max_visible_subtitles-(1 if self.full_text else 0)); self.history_lines=self.history_lines[-keep:] if keep else []; return 0
    def update(self): self.updated+=1
ns={'ControlPanel':ControlPanel,'LyricWindow':LyricWindow,'write_error_log':write_error_log}
exec(compile(block,'<h33>','exec'),ns,ns); ns['_h33_activate_runtime']()
assert getattr(ControlPanel._auto_transport_hint_active,'_limbus_layer','')=='H33'
assert getattr(LyricWindow.check_lyric_time,'_limbus_layer','')=='H33'
# A hint is valid only for the selected player epoch that created it.
p=ControlPanel(); p._note_auto_transport_hint('qq-gsmtc-fast-event',1.8); assert p._auto_transport_hint_active() is True
p.player_combo.name='网易云音乐'; p.media_sync._media_player_epoch=2
assert p._auto_transport_hint_active() is False
assert p._auto_transport_hint_source=='' and p._auto_transport_hint_until==0.0
# New player can create its own fresh hint normally.
p._note_auto_transport_hint('netease-native-track-edge',1.8); assert p._auto_transport_hint_active() is True
# QQ direct provider-idle landing preserves already-held history under configured capacity.
w=LyricWindow(True); out=w.check_lyric_time(); assert out=='legacy-return'; assert w.history_lines==['h1','h2'],w.history_lines
assert w.full_text=='' and w._provider_idle_suppressed_line==7 and w.updated>=1
# Non-QQ behavior remains historical.
n=LyricWindow(False); n.check_lyric_time(); assert n.history_lines==[]
print('QQ CAPACITY + PLAYER EPOCH H33 REPLAY: PASS')
print(' - QQ direct provider-idle landing preserves held multi-subtitle history')
print(' - history remains bounded by max_visible_subtitles capacity')
print(' - transport hints are owned by player name + MediaSync player epoch')
print(' - a QQ hint cannot accelerate NetEase after a player switch')
print(' - non-QQ direct-idle behavior remains unchanged')
