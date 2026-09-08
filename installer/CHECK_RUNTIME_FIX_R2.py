from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from limbus_core import CircuitBreaker, CircuitOpen, advancing_time_pair_step


def main_source() -> Path:
    rows = sorted(ROOT.glob('LimbusLyric_v1.8.9.133_CROSS_PROVIDER*.py'))
    assert len(rows) == 1, rows
    return rows[0]


def check_breaker():
    b = CircuitBreaker(threshold=2, open_ms=45000)
    assert b.allow('qq', now_ms=1000)
    assert not b.failure('qq', now_ms=1000)
    assert b.failure('qq', now_ms=1100)
    assert not b.allow('qq', now_ms=1200)
    try:
        b.require('qq', now_ms=1200)
    except CircuitOpen:
        pass
    else:
        raise AssertionError('open circuit must reject without network call')
    assert b.allow('qq', now_ms=46101)
    b.success('qq')
    assert b.snapshot('qq', now_ms=46102)['failures'] == 0


def check_advancing_pair():
    p = None
    proven = False
    for i in range(5):
        p, proven = advancing_time_pair_step(p, i * 1000, 242000, i * 1000, 'playing', 'pair-a')
    assert proven, p
    p = None
    for i in range(8):
        p, proven = advancing_time_pair_step(p, 42000, 242000, i * 300, 'playing', 'pair-a')
        assert not proven
    p, proven = advancing_time_pair_step(None, 1000, 242000, 0, 'paused', 'pair-a')
    assert p is None and not proven


def check_source_contracts():
    text = main_source().read_text(encoding='utf-8')
    tree = ast.parse(text)
    assert '_r2_qq_search_request' in text
    assert text.count('client_search_cp') >= 5
    # R9.2: the current QQ desktop search API is primary; the legacy endpoint stays standby.
    assert 'DoSearchForQQMusicDesktop' in text
    assert 'https://u.y.qq.com/cgi-bin/musicu.fcg' in text
    assert 'R9.2 QQ现代搜索接管' in text
    assert "globals()['_r2_qq_search_request'] = _r9_2_qq_search_request" in text
    assert 'R2 QQ推进时钟自证播放器时长' in text
    assert 'duration_self_proved' in text
    assert 'R2跨平台逐字候选等待播放器版本证明' in text
    assert "duration = 0 if provisional_version" in text
    assert 'R2酷狗后台时钟Holdover' in text
    assert 'R2酷狗播放实例视觉Epoch切换' in text
    assert '_r2_kugou_visual_quarantine_until_mono' in text
    assert '30000.0, 30000.0' in text
    # R2 must not recreate the S3/S4 consolidation mistake.
    forbidden = ['_LIMBUS_S3_SEARCH_STAGES', '_LIMBUS_S4_CONTROL_INIT_CURRENT']
    for name in forbidden:
        assert name not in text, name
    # Ensure the new renderer reset is inside the mature check_lyric_time method, not a new wrapper.
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'LyricWindow')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'check_lyric_time')
    body = ast.get_source_segment(text, fn) or ''
    assert 'R2酷狗播放实例视觉Epoch切换' in body
    assert 'self.lyric_timeline' in body and 'self.history_lines = []' in body


if __name__ == '__main__':
    check_breaker()
    check_advancing_pair()
    check_source_contracts()
    print('RUNTIME FIX R2: PASS')
