from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from limbus_core import (
    FaultJournal,
    LyricQuery,
    PlaybackSnapshot,
    ProviderRegistry,
    choose_bilingual_pair,
    duration_compatible,
    provider_order,
)


class FakeEngine:
    last_error = ''
    meta = {}
    calls = []

    @classmethod
    def _set_provider_meta(cls, **kwargs):
        cls.meta = dict(kwargs)

    @classmethod
    def last_provider_meta(cls):
        return dict(cls.meta)

    @classmethod
    def search_netease(cls, song, artist, **kwargs):
        cls.calls.append(('netease-precise', song, artist, dict(kwargs)))
        cls.meta.update(song_id='n1')
        return '[00:00.00](0,100)你', '[00:00.00]you', 100000

    @classmethod
    def _search_netease_ordinary(cls, song, artist, **kwargs):
        cls.calls.append(('netease-ordinary', song, artist, dict(kwargs)))
        return '[00:00.00]你', None, 100000

    @classmethod
    def search_qq(cls, song, artist, **kwargs):
        cls.calls.append(('qq-precise', song, artist, dict(kwargs)))
        return '[00:00.00](0,100)你', None, 100100

    @classmethod
    def _search_qq_ordinary(cls, song, artist, **kwargs):
        cls.calls.append(('qq-ordinary', song, artist, dict(kwargs)))
        return '[00:00.00]你', None, 100100

    @classmethod
    def search_kugou(cls, song, artist, **kwargs):
        cls.calls.append(('kugou-precise', song, artist, dict(kwargs)))
        return '[00:00.00](0,100)你', None, 99900

    @classmethod
    def _search_kugou_ordinary(cls, song, artist, **kwargs):
        cls.calls.append(('kugou-ordinary', song, artist, dict(kwargs)))
        return '[00:00.00]你', None, 99900


def check_provider_registry():
    FakeEngine.calls = []
    reg = ProviderRegistry.from_legacy_engine(FakeEngine)
    assert reg.names() == ('网易云', 'QQ音乐', '酷狗')
    r = reg.fetch(LyricQuery(
        song='Song', artist='Artist', provider='网易云', expected_duration_ms=100000,
        provider_track_id='abc', provider_duration_ms=100000, prefer_precise=True, borrow=False,
    ))
    assert r.duration_ms == 100000 and r.provider == '网易云'
    name, _, _, kw = FakeEngine.calls[-1]
    assert name == 'netease-precise'
    assert kw['preferred_song_id'] == 'abc' and kw['strict_identity'] is False
    r = reg.fetch(LyricQuery(
        song='Song', artist='Artist', provider='网易云', expected_duration_ms=100000,
        provider_track_id='abc', provider_duration_ms=100000, prefer_precise=False, borrow=True,
    ))
    name, _, _, kw = FakeEngine.calls[-1]
    assert name == 'netease-ordinary'
    assert kw['preferred_song_id'] is None and kw['preferred_duration_ms'] == 0
    assert kw['strict_identity'] is True
    reg.fetch(LyricQuery(song='Song', provider='QQ音乐', expected_duration_ms=100000, prefer_precise=False))
    assert FakeEngine.calls[-1][0] == 'qq-ordinary'
    reg.fetch(LyricQuery(song='Song', provider='酷狗', expected_duration_ms=100000, prefer_precise=True))
    assert FakeEngine.calls[-1][0] == 'kugou-precise'


def check_playback_contract():
    raw = {
        'connected': 1, 'status': 'PLAYING', 'position_ms': 1234.4,
        'duration_ms': 99999.6, 'position_source': 'gsmtc', 'media_title': 'X',
        'media_artist': 'Y', 'media_source': 'qqmusic.exe', 'sync_waiting': 0,
        'qq_transport_status': 'unknown-motion', 'custom_evidence': {'a': 1},
    }
    snap = PlaybackSnapshot.from_legacy(raw, captured_mono_ms=12.5)
    assert snap.status == 'playing' and snap.position_ms == 1234 and snap.duration_ms == 100000
    assert snap.extras['qq_transport_status'] == 'unknown-motion'
    out = snap.to_legacy()
    assert out['custom_evidence'] == {'a': 1} and out['position_source'] == 'gsmtc'
    assert snap.has_clock


def check_policy():
    assert provider_order('QQ音乐') == ('QQ音乐', '网易云', '酷狗')
    assert duration_compatible(100000, 102500)
    assert not duration_compatible(100000, 110000)
    rows = [
        {'provider': '网易云', 'coverage': .99, 'quality': 1, 'trans_rows': 10},
        {'provider': 'QQ音乐', 'coverage': .92, 'quality': 3, 'trans_rows': 9},
    ]
    assert choose_bilingual_pair(rows, '网易云', True)['provider'] == 'QQ音乐'


def check_fault_journal():
    j = FaultJournal(8)
    for i in range(12):
        try:
            raise ValueError('fault-%d' % i)
        except Exception as exc:
            j.record('test', exc, detail=str(i))
    rows = j.snapshot()
    assert len(rows) == 8
    assert rows[-1]['message'] == 'fault-11' and rows[0]['message'] == 'fault-4'


if __name__ == '__main__':
    check_provider_registry()
    check_playback_contract()
    check_policy()
    check_fault_journal()
    print('STABILIZATION CONTRACT S2: PASS')
