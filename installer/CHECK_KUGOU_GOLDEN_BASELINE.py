from __future__ import annotations
import ast, hashlib, sys
from pathlib import Path
# 2026-09-08 R2.1: transport-scoped gesture invalidation reviewed; stale gesture evidence cannot cross a transport generation.
# 2026-09-08 R2: user rail gesture explicitly clears only the new visual-rail quarantine;
# gesture target/seek authority itself is unchanged and remains covered by the KuGou seek replays.
# H8F1: KuGou gesture hot paths are re-locked after all synchronous window discovery was removed; seek/rail authority semantics are unchanged.
EXPECTED = {'AsyncPlayerUiPositionReader.set_kugou_numeric_seek_hint': '948786957a7da91aecd849ef273fc1a471120f03d0f5bea0868124df3aa221e7', 'LyricFetcher.get_kugou_ui_duration_hint': '1d0d70cdbcc5531aec591124b003b6a2a93fc5d50d11ff9b6949b9cd92bd9694', 'LyricSearchEngine._fetch_strict_kugou_word_match': '46987fbfb180c6f70bc5ca715605546357974711a4f0f94ad689b9141c18fa73', 'LyricSearchEngine.search_kugou': 'b318f7b2a5a24646ce419b5a545daa7b5c1b696e43207f5b3cea8549e82c85fb', 'MediaSessionSync._ensure_kugou_mouse_hook': '21529956977693ddd98a22639b4298d535151915fbc41ac461ecdbde8af4ddeb', 'MediaSessionSync._kugou_commit_gesture_seek': '8625b6bd6310bd55878fea59a90cdea4d8fd80fb3cc913455aa147854256fc06', 'MediaSessionSync._kugou_consume_hooked_mouse_events': '0da9ee784787d5af95ad3f7e76e81f2d1a0421d5fa89333babec9d39035d11d9', 'MediaSessionSync._kugou_hotpath_cached_window_rect': '5c26e4bf1feafee5cf147387bdbbbdc3479c8d9996d6d4d775fa3c7aa9f8e79b', 'MediaSessionSync._kugou_poll_pointer_gesture': '7c63fc7248ca8beebc1d6b6908fb8712ee000bd40004c016509d589e21beb805', 'MediaSessionSync._kugou_select_public_clock': 'a0b8c970f0286eb3659cd19f36aaf392582679c5f29584d633d37e0eca24a9ce', 'MediaSessionSync._kugou_target_from_cursor': '3e76e8457a7cb2ab8022e30ba8676a31127cc822f9f2383b52fe945b1adc1130', 'MediaSessionSync._kugou_window_rect': '37ad0bfafbe5af8e03b52ddf6b763a60cecd94d72aeefcdd64a2e298dbeab84d', 'PlayerUiPositionReader._is_kugou_process': 'b73b3eb7a75ff050793c5cc4c0575ed6745d5640009fcee17a4fad5ed2545007', 'PlayerUiPositionReader._try_kugou_memory_clock_probe': '8c81d0f09cb3f3639ce1e9cecd126f14fefe08092a4f1d3738c3820e91fc5a3b', 'PlayerUiPositionReader._try_kugou_msaa_probe': '50c27d5f06b846fdfbbd5c11b40f77c1a5a85bb3fa6e51d4f3cded3aa1076aa0', 'PlayerUiPositionReader._try_kugou_numeric_memory_clock': 'ba2e69a214cef2d4b7af337e4ecc2fda6f51d07bdb26cf29c6d6e88921737dd1', 'PlayerUiPositionReader._try_kugou_point_probe': '71c87a736c58601927509fb3ce8faa8c74ab25a4d1ca3b3714b3994a477ef65f', 'PlayerUiPositionReader._try_kugou_win32_probe': 'f680cd74b9796232a59a4fdd6f28ef14cc0bb7167dd47c1bb7ea2f42bfd4bf25', 'PlayerUiPositionReader.kugou_main_window_rect': '9fd4f3beb31fa57104a7fcfee89539d98e8d2edf7cf5c0fbb0047eba6848583b', 'PlayerUiPositionReader.reject_kugou_numeric_anchor': 'c3fa539fca52b41c2e81559784263257c25b0bdb8f30a40f0ce68ca2218a8d31', 'PlayerUiPositionReader.set_kugou_numeric_seek_hint': '58120bc166a452ebcb4dbf0aa802e78b780e7bdf08b08ebc881779ba10db599c', '_decode_kugou_krc_content': 'f5a8dcaf8a175b09b4fc4604355a120e1aba55a1f7f4a8374e39da6b164d0a58'}
if len(sys.argv)!=2:
    print('usage: CHECK_KUGOU_GOLDEN_BASELINE.py <main.py>'); raise SystemExit(2)
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8')

def collect(text):
    tree=ast.parse(text, filename=str(path)); out={}
    def walk(body,p=''):
        for n in body:
            if isinstance(n,ast.ClassDef): walk(n.body, f'{p}.{n.name}' if p else n.name)
            elif isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): out[f'{p}.{n.name}' if p else n.name]=n
    walk(tree.body); return out

def segment(text,node):
    lines=text.splitlines(); return '\n'.join(lines[node.lineno-1:node.end_lineno]).rstrip()+'\n'
funcs=collect(source); failures=[]
for q,expected in EXPECTED.items():
    n=funcs.get(q)
    if n is None: failures.append(q+': missing'); continue
    actual=hashlib.sha256(segment(source,n).encode('utf-8')).hexdigest()
    if actual!=expected: failures.append(q+': source changed')
# Also reject the provisional layer that caused the regression.
for token in ('arm_kugou_manual_provisional','disarm_kugou_manual_provisional','_reset_kugou_provisional_state',
              'KUGOU_NUMERIC_PAUSE_PROOF_ENABLED','KUGOU_NUMERIC_CONTINUOUS_PROOF_ENABLED','KUGOU_NUMERIC_VALIDATOR_VERSION'):
    if token in source: failures.append('reverted KuGou layer returned: '+token)
if failures:
    print('KUGOU GOLDEN BASELINE: FAIL')
    for x in failures: print('  - '+x)
    raise SystemExit(29)
print(f'KUGOU GOLDEN BASELINE: PASS ({len(EXPECTED)} source-locked methods)')
print('  lock=normalized-source-sha256 (CPython-version independent; no ast.dump fingerprint)')
