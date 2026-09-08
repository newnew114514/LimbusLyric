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
        print('usage: CHECK_QQ_POST_RAIL_TREND_RECOVERY_H10F4_REPLAY.py <main.py>')
        return 2
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    funcs = collect(source)
    q = 'MediaSessionSync._qq_note_unarmed_far_seek'
    if q not in funcs:
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print('  - production helper missing')
        return 41

    code = textwrap.dedent(funcs[q]).replace('def _qq_note_unarmed_far_seek', 'def replay', 1)
    logs = []
    g = {
        'QQ_LYRIC_TEXT_SEEK_ENABLED': True,
        'QQ_LYRIC_TEXT_TARGET_TOLERANCE_MS': 1700.0,
        'QQ_POST_RAIL_UNARMED_STALE_WINDOW_MS': 12500.0,
        'QQ_POST_RAIL_UNARMED_STALE_MIN_BACK_MS': 2200.0,
        'QQ_POST_RAIL_CONFLICT_MIN_DELTA_MS': 4200.0,
        'QQ_POST_RAIL_CONFLICT_HINT_TOL_MIN_MS': 3600.0,
        'QQ_POST_RAIL_CONFLICT_HINT_TOL_RATIO': 0.025,
        'QQ_POST_RAIL_CONFLICT_HINT_TOL_MAX_MS': 6500.0,
        'QQ_POST_RAIL_CONFLICT_RECOVERY_MIN_SAMPLES': 3,
        'QQ_POST_RAIL_CONFLICT_RECOVERY_MIN_SPAN_MS': 900.0,
        'QQ_POST_RAIL_CONFLICT_RECOVERY_MAX_OUTLIERS': 2,
        'SOURCE_GUARD_ENABLED': True,
        'write_error_log': lambda *a, **k: logs.append((a, k)),
    }
    exec(code, g)
    replay = g['replay']

    class Dummy:
        _uia_duration_ms = 142000
        _qq_lyric_click_target_until_mono = 0.0
        _qq_lyric_click_target_ms = None
        _qq_unarmed_far_pending = None
        _qq_nonrail_click_until_mono = 0.0
        _qq_last_rail_commit_mono = 1000.0
        _qq_last_rail_commit_target = 11420.0
        _qq_last_rail_visual_hint_ms = 2589.0
        _qq_last_rail_visual_hint_mono = 1000.0
        _qq_post_rail_stale_last_log_mono = 0.0

    # Replay the 2026-08-21 "但" shape: the rail geometry says ~2.6s but the first UIA
    # commit latched ~11.4s. The real Text stream restarts near 0s and advances normally,
    # with a single unrelated 37s Text outlier interleaved. Recovery must preserve the
    # 0->1->2s main trend and commit within ~2s instead of waiting out the 12.5s veto.
    d = Dummy()
    seq = [
        (0.0, 11600.0, 1200.0),
        (1000.0, 12600.0, 2200.0),
        (37000.0, 13000.0, 2600.0),
        (2000.0, 13600.0, 3200.0),
    ]
    result = None
    for obs, pred, now in seq:
        v = replay(d, obs, pred, 142000, 'playing', 'pair', now)
        if v is not None:
            result = v
    if result is None or abs(float(result) - 2420.0) > 50.0:
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print(f'  - geometry-conflicted 0->1->[37]->2 stream did not recover: {result!r}')
        return 42
    if not any(a and a[0] == 'QQ Rail冲突恢复忽略孤立Text离群' for a, _ in logs):
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print('  - isolated outlier was not explicitly quarantined')
        return 43
    if not any(a and a[0] == 'QQ Rail提交冲突趋势恢复提交' for a, _ in logs):
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print('  - conflict recovery commit diagnostic missing')
        return 44

    # The original host-safe case must remain blocked: a correct 51.420s rail commit and
    # delayed 54->55s old Text stream ~10s later must NOT accumulate unarmed evidence.
    logs.clear()
    d2 = Dummy()
    d2._uia_duration_ms = 221000
    d2._qq_last_rail_commit_target = 51420.0
    d2._qq_last_rail_visual_hint_ms = 51420.0
    d2._qq_unarmed_far_pending = None
    if replay(d2, 54000, 61311, 221000, 'playing', 'pair', 11000.0) is not None:
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print('  - host-safe delayed 54s old stream committed')
        return 45
    if replay(d2, 55000, 61701, 221000, 'playing', 'pair', 11600.0) is not None:
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print('  - host-safe delayed 55s old stream committed')
        return 46
    if d2._qq_unarmed_far_pending is not None:
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print('  - host-safe old stream accumulated evidence')
        return 47

    # A large UIA/geometry disagreement alone is not enough. If the observed stream is not
    # near the physical rail timeline, it must stay quarantined.
    d3 = Dummy()
    d3._qq_unarmed_far_pending = None
    v = replay(d3, 54000, 61311, 142000, 'playing', 'pair', 11000.0)
    if v is not None or d3._qq_unarmed_far_pending is not None:
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print('  - unrelated far stream bypassed physical-rail plausibility gate')
        return 48

    # No geometry hint => no new exception. This preserves old builds/missing-geometry safety.
    d4 = Dummy()
    d4._qq_last_rail_visual_hint_ms = None
    d4._qq_unarmed_far_pending = None
    replay(d4, 0, 11600, 142000, 'playing', 'pair', 1200.0)
    if d4._qq_unarmed_far_pending is not None:
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print('  - missing rail hint incorrectly entered conflict recovery')
        return 49

    if 'QQ POST-RAIL TREND RECOVERY H10F4' not in source:
        print('QQ POST-RAIL TREND RECOVERY H10F4: FAIL')
        print('  - H10F4 build marker missing')
        return 50

    print('QQ POST-RAIL TREND RECOVERY H10F4: PASS')
    print('  geometry/UIA conflict 0->1->[37]->2 recovers in ~2s: PASS')
    print('  isolated Text outlier does not erase main trend: PASS')
    print('  original 51.420s -> delayed 54/55s host-safe veto preserved: PASS')
    print('  unrelated far stream remains quarantined: PASS')
    print('  missing rail geometry cannot use recovery exception: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
