from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path


def collect(text: str):
    tree = ast.parse(text)
    lines = text.splitlines()
    out = {}

    def walk(body, prefix=''):
        for node in body:
            if isinstance(node, ast.ClassDef):
                walk(node.body, f'{prefix}.{node.name}' if prefix else node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = f'{prefix}.{node.name}' if prefix else node.name
                out[q] = '\n'.join(lines[node.lineno - 1:node.end_lineno]) + '\n'

    walk(tree.body)
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: CHECK_QQ_HOST_SAFE_REPLAY.py <main.py>')
        return 2
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    funcs = collect(source)
    required = {
        '_qq_initial_anchor_stream_step',
        'MediaSessionSync._qq_note_unarmed_far_seek',
        'MediaSessionSync._qq_rebase_auto_local_from_coherent_uia',
    }
    missing = sorted(required - funcs.keys())
    if missing:
        print('QQ HOST-SAFE REPLAY: FAIL')
        for q in missing:
            print('  - missing ' + q)
        return 41

    # Replay the host log's safe provisional proof: an advancing validated stream passes;
    # a static hover preview with the same duration cannot.
    g = {
        'QQ_HOVER_SAFE_CLOCK_MAX_GAP_MS': 1500.0,
        'QQ_INITIAL_ANCHOR_MIN_PROGRESS_MS': 500.0,
        'QQ_INITIAL_ANCHOR_MAX_PACE_ERROR_MS': 900.0,
        'QQ_INITIAL_ANCHOR_MIN_CONFIDENCE': 160,
        'QQ_INITIAL_ANCHOR_MIN_SAMPLES': 3,
        'QQ_INITIAL_ANCHOR_MIN_SPAN_MS': 520.0,
    }
    exec(funcs['_qq_initial_anchor_stream_step'], g)
    step = g['_qq_initial_anchor_stream_step']
    pending = None
    proven = False
    for raw, now in ((38000, 0), (39000, 610), (40000, 1210)):
        pending, proven = step(
            pending, raw, now, 'playing', 'qq-time-pair-validated', 'pair', 168
        )
    if not proven:
        print('QQ HOST-SAFE REPLAY: FAIL')
        print('  - 38->39->40 advancing validated stream did not prove provisional clock')
        return 42

    pending = None
    static_proven = False
    for raw, now in ((78000, 0), (78000, 620), (78000, 1240), (78000, 1860)):
        pending, static_proven = step(
            pending, raw, now, 'playing', 'qq-time-pair-validated', 'pair', 168
        )
    if static_proven:
        print('QQ HOST-SAFE REPLAY: FAIL')
        print('  - static hover preview incorrectly proved provisional clock')
        return 43

    # Replay 02:01:30 rail commit followed by the delayed 54->55s old stream while local
    # prediction is already ~61-62s. The unarmed detector must keep its pending state empty.
    code = textwrap.dedent(funcs['MediaSessionSync._qq_note_unarmed_far_seek']).replace(
        'def _qq_note_unarmed_far_seek', 'def replay_unarmed', 1
    )
    logs = []
    g2 = {
        'QQ_LYRIC_TEXT_SEEK_ENABLED': True,
        'QQ_LYRIC_TEXT_TARGET_TOLERANCE_MS': 1700.0,
        'QQ_POST_RAIL_UNARMED_STALE_WINDOW_MS': 12500.0,
        'QQ_POST_RAIL_UNARMED_STALE_MIN_BACK_MS': 2200.0,
        'write_error_log': lambda *a, **k: logs.append((a, k)),
    }
    exec(code, g2)
    replay = g2['replay_unarmed']

    class Dummy:
        _uia_duration_ms = 221000
        _qq_lyric_click_target_until_mono = 0.0
        _qq_lyric_click_target_ms = None
        _qq_unarmed_far_pending = None
        _qq_nonrail_click_until_mono = 0.0
        _qq_last_rail_commit_mono = 1000.0
        _qq_post_rail_stale_last_log_mono = 0.0

    d = Dummy()
    if replay(d, 54000, 61311, 221000, 'playing', 'pair', 11000.0) is not None:
        print('QQ HOST-SAFE REPLAY: FAIL')
        print('  - delayed 54s old stream committed')
        return 44
    if replay(d, 55000, 61701, 221000, 'playing', 'pair', 11600.0) is not None:
        print('QQ HOST-SAFE REPLAY: FAIL')
        print('  - delayed 55s old stream committed')
        return 45
    if d._qq_unarmed_far_pending is not None:
        print('QQ HOST-SAFE REPLAY: FAIL')
        print('  - delayed old stream was allowed to accumulate unarmed evidence')
        return 46
    if not logs or logs[-1][0][0] != 'QQ Seek后迟到旧流隔离':
        print('QQ HOST-SAFE REPLAY: FAIL')
        print('  - delayed old stream quarantine diagnostic missing')
        return 47

    # Outside the recent-rail window the original unarmed trend path must still be usable.
    d2 = Dummy()
    d2._qq_last_rail_commit_mono = 1.0
    results = []
    for obs, now, pred in ((54000, 20000, 62000), (55000, 21000, 63000), (56000, 22000, 64000)):
        results.append(replay(d2, obs, pred, 221000, 'playing', 'pair', now))
    if not any(v is not None for v in results):
        print('QQ HOST-SAFE REPLAY: FAIL')
        print('  - ordinary unarmed seek outside rail protection window became impossible')
        return 48

    print('QQ HOST-SAFE REPLAY: PASS')
    print('  advancing 38->39->40 provisional proof: PASS')
    print('  static hover 78->78->78 rejected: PASS')
    print('  recent rail delayed 54->55 old stream quarantined: PASS')
    print('  ordinary unarmed seek outside rail window still confirmable: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
