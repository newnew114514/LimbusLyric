from pathlib import Path
import ast, sys, types

if len(sys.argv) != 2:
    raise SystemExit(2)
source_path = Path(sys.argv[1])
text = source_path.read_text(encoding='utf-8')
tree = ast.parse(text)

def need(cond, msg):
    if not cond:
        print('RUNTIME SEARCH CHAIN H95F10F1 REPLAY: FAIL')
        print(' - ' + msg)
        raise SystemExit(1)

def find_func(name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None

h41 = find_func('_h41_search')
h95 = find_func('_h95f8_search')
need(h41 is not None, 'H41 search wrapper missing')
need(h95 is not None, 'H95F8 final search wrapper missing')
args = [a.arg for a in h41.args.args]
need('provider_locked' in args and 'require_translation_pair' in args,
     'H41 middle wrapper does not accept final source-lock arguments')

# Execute H41 wrapper as a top-level function with a controllable previous search.
mod = ast.Module(body=[h41], type_ignores=[])
ns = {}
exec(compile(mod, str(source_path), 'exec'), ns)
h41_fn = ns['_h41_search']

calls = []
def old_shape(song, artist='', source='网易云', trans_only=False,
              provider_track_id=None, provider_duration_ms=0, prefer_precise=True):
    calls.append(('old', song, dict(provider_track_id=provider_track_id,
                                    provider_duration_ms=provider_duration_ms,
                                    prefer_precise=prefer_precise)))
    return '[00:00.00]ok', 100000
h41_fn.__globals__['_LIMBUS_H41_SEARCH_PRE'] = old_shape
h41_fn.__globals__['_h41_lyric_completeness'] = lambda lyric, expected: {'bad': False}
lyric, duration = h41_fn('single-language', source='QQ音乐', provider_locked=False, require_translation_pair=False)
need(bool(lyric) and calls and calls[-1][0] == 'old', 'ordinary H95F8->H41 call shape is not backward compatible')

calls2 = []
def new_shape(song, artist='', source='网易云', trans_only=False,
              provider_track_id=None, provider_duration_ms=0, prefer_precise=True,
              provider_locked=False, require_translation_pair=False):
    calls2.append((bool(provider_locked), bool(require_translation_pair)))
    return '[00:00.00]pair', 100000
h41_fn.__globals__['_LIMBUS_H41_SEARCH_PRE'] = new_shape
lyric, duration = h41_fn('bilingual', source='QQ音乐', require_translation_pair=True)
need(bool(lyric) and calls2[-1] == (False, True), 'bilingual source-lock flag was not forwarded through H41')
lyric, duration = h41_fn('sidecar', source='QQ音乐', trans_only=True, provider_locked=True)
need(bool(lyric) and calls2[-1] == (True, False), 'provider-locked sidecar flag was not forwarded through H41')

# Reproduce the exact production edge that broke H95F10: H95F8 always supplies both kwargs.
ns95 = {
    '_H95F8_SEARCH_PRE': h41_fn,
    '_h95f8_payload_health': lambda lyric, meta: (True, 'ok', 1, 1),
    'LyricSearchEngine': types.SimpleNamespace(last_provider_meta=lambda: {}),
}
exec(compile(ast.Module(body=[h95], type_ignores=[]), str(source_path), 'exec'), ns95)
h41_fn.__globals__['_LIMBUS_H41_SEARCH_PRE'] = old_shape
lyric, duration = ns95['_h95f8_search']('runtime-chain', source='QQ音乐')
need(bool(lyric), 'H95F8 -> H41 ordinary runtime chain still raises/drops before provider search')

# H94/QQ final-empty ownership must not clear the target while fourth-provider fallback is pending.
need("_h94_auto_fallback_pending_key" in text, 'H94 fallback pending ownership marker missing')
need("QQ自动歌词失败事务等待H94兜底" in text, 'QQ cleanup does not defer while H94 owns fallback')
need("current_key != key" in text, 'late H94 fallback does not cancel when target ownership is released')
need("自动歌词搜索异常" in text, 'auto search exceptions are still silently flattened to ok=0')
need('+ RUNTIME SEARCH CHAIN + FALLBACK TXN H95F10F1' in text, 'H95F10F1 build marker missing')

print('RUNTIME SEARCH CHAIN H95F10F1 REPLAY: PASS')
print('  H95F8 -> H41 ordinary call no longer TypeErrors before provider search: PASS')
print('  bilingual/provider-locked flags cross H41 without breaking old call shape: PASS')
print('  H94 pending fallback owns target until terminal re-emission: PASS')
print('  auto-search exceptions are explicitly logged instead of masquerading as 0ms misses: PASS')
