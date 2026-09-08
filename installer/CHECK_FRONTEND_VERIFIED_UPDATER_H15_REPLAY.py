#!/usr/bin/env python3
from pathlib import Path
import ast, hashlib, os, re, sys, tempfile, urllib.parse

root = Path(__file__).resolve().parents[1]
main = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
src = main.read_text(encoding='utf-8-sig')
marker = '# H15 frontend integration / verified installer update'
main_guard = '\nif __name__ == "__main__":\n'
assert marker in src, 'H15 marker missing'
assert main_guard in src, 'main guard missing'
assert src.index(marker) < src.index(main_guard), 'H15 closure must install before main guard'
assert 'FRONTEND POLISH R4 + VERIFIED INSTALLER UPDATE H15' in src

# R4 shell remains present and H15 integrates runtime-added H12/H13 cards.
for token in (
    'self.top_nav = QFrame()', 'self.settings_filter = QLineEdit()',
    "self.settings_filter.setPlaceholderText(\"搜索当前页设置…\")",
    "card.findChildren(QLabel, 'sectionTitle', Qt.FindDirectChildrenOnly)",
    "baseline[idx] = (known_layout, (16, 15, 16, 16, 10))",
    "_h12_apply_scale(panel, int(getattr(panel, '_h12_ui_scale_pct', 100) or 100))",
):
    assert token in src, f'frontend integration token missing: {token}'

# Complete updater contract: replace H12 checker at runtime, require verified SHA-256,
# stream to a .part file, atomically publish, launch external installer, bounded-exit app.
for token in (
    "DEFAULT_UPDATE_API_URL = 'https://api.github.com/repos/newnew114514/LimbusLyric/releases/latest'",
    "FEEDBACK_EMAIL = '1826555940@qq.com'",
    'H15_AUTO_CHECK_INTERVAL_SEC = 24 * 60 * 60',
    "QTimer.singleShot(H15_AUTO_CHECK_DELAY_MS, lambda p=self: _h15_maybe_auto_check(p))",
    "globals()['_h12_check_update'] = _h15_check_update",
    "globals()['_h12_poll_async'] = _h15_poll_async",
    'H15_UPDATE_MAX_BYTES = 512 * 1024 * 1024',
    "part_path = final_path + '.part'",
    'hasher = hashlib.sha256()',
    "if actual != digest:",
    'os.replace(part_path, final_path)',
    'subprocess.Popen([path]',
    'QTimer.singleShot(250, panel._exit_app)',
    "response.iter_content(chunk_size=H15_UPDATE_CHUNK_BYTES)",
    "if not _h15_https(getattr(response, 'url', url)):",
):
    assert token in src, f'updater safety token missing: {token}'

# Support resources are local so the support dialog does not depend on GitHub/browser access.
for asset_name in ('alipay_support.png', 'wechat_support.png'):
    asset = root / 'support_assets' / asset_name
    assert asset.is_file() and asset.stat().st_size > 1000, f'support asset missing/empty: {asset_name}'
spec = (root / 'installer' / 'LimbusLyric.spec').read_text(encoding='utf-8-sig')
assert "support_dir = ROOT / 'support_assets'" in spec and "datas.append((str(asset), 'support_assets'))" in spec
assert 'Qt.FastTransformation' in src, 'support QR display must keep hard edges for reliable scanning'

# Extract and execute the pure parser/version helpers without importing Qt/main program.
tree = ast.parse(src)
needed = {
    '_h15_version_key', '_h15_current_version_label', '_h15_https', '_h15_digest',
    '_h15_safe_installer_name', '_h15_release_candidate', '_h15_update_status',
    '_h15_download_installer_file',
}
ns = {
    're': re, 'urllib': urllib, 'os': os, 'hashlib': hashlib,
    'H15_UPDATE_MAX_BYTES': 512 * 1024 * 1024, 'H15_UPDATE_CHUNK_BYTES': 1024 * 1024,
    'LIMBUSLYRIC_BUILD_TAG': 'v1.8.9.133 RC11 + H10F4 + H14 + FRONTEND POLISH R4 + VERIFIED INSTALLER UPDATE H15',
}
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in needed:
        module = ast.Module(body=[node], type_ignores=[])
        ast.fix_missing_locations(module)
        exec(compile(module, str(main), 'exec'), ns, ns)
missing = needed.difference(ns)
assert not missing, f'pure H15 helpers missing: {sorted(missing)}'

key = ns['_h15_version_key']
assert key('v1.8.9.133 H10F4') < key('v1.8.9.133 H14') < key('v1.8.9.133 H15')
assert key('v1.8.9.133 H99') < key('v1.8.9.134')
assert ns['_h15_current_version_label']() == '1.8.9.133 H15'
assert ns['_h15_https']('https://example.com/a')
assert not ns['_h15_https']('http://example.com/a')
assert not ns['_h15_https']('file:///tmp/a')
assert ns['_h15_digest']('sha256:' + 'A'*64) == 'a'*64
assert ns['_h15_digest']('sha1:' + 'a'*64) == ''

release = {
    'tag_name': 'v1.8.9.134 H16',
    'html_url': 'https://github.com/example/LimbusLyric/releases/tag/v1.8.9.134',
    'body': 'new things',
    'assets': [
        {'name': 'notes.txt', 'browser_download_url': 'https://github.com/x/notes.txt', 'digest': 'sha256:' + 'b'*64, 'size': 10},
        {'name': 'LimbusLyric_Setup_1.8.9.134.exe', 'browser_download_url': 'https://github.com/example/LimbusLyric/releases/download/v/setup.exe', 'digest': 'sha256:' + 'c'*64, 'size': 123456},
    ],
}
c = ns['_h15_release_candidate'](release)
assert c['newer'] is True and c['verified_installer'] is True, c
assert c['installer_sha256'] == 'c'*64
assert c['installer_name'] == 'LimbusLyric_Setup_1.8.9.134.exe'
assert c['installer_size'] == 123456
assert 'SHA-256 已验证' in ns['_h15_update_status'](c)

# Missing digest must never become executable auto-update; manual page stays available.
no_digest = dict(release)
no_digest['assets'] = [dict(release['assets'][1], digest='')]
c2 = ns['_h15_release_candidate'](no_digest)
assert c2['newer'] is True and c2['verified_installer'] is False
assert c2['page_url'].startswith('https://')
assert '仅允许打开下载页' in ns['_h15_update_status'](c2)

# Non-HTTPS installer is dropped even with a syntactically valid digest.
bad = {
    'version': '1.8.9.134', 'page_url': 'https://example.com/release',
    'installer_url': 'http://example.com/LimbusLyric_Setup.exe',
    'installer_sha256': 'd'*64,
}
c3 = ns['_h15_release_candidate'](bad)
assert c3['verified_installer'] is False and c3['installer_url'] == ''

# Old or equal releases never arm the install button contract.
c4 = ns['_h15_release_candidate']({'version':'1.8.9.133 H14','page_url':'https://example.com/release'})
assert c4['newer'] is False


# Execute the real downloader against fake streaming responses. This covers the byte/hash path,
# not only source-token assertions.
class FakeResponse:
    def __init__(self, data=b'', url='https://cdn.example/LimbusLyric_Setup.exe', status_ok=True, header_size=None):
        self.data = bytes(data); self.url = url; self.status_ok = status_ok
        self.headers = {'Content-Length': str(len(self.data) if header_size is None else header_size)}
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def raise_for_status(self):
        if not self.status_ok: raise RuntimeError('HTTP failure')
    def iter_content(self, chunk_size=1024):
        for i in range(0, len(self.data), max(1, int(chunk_size))):
            yield self.data[i:i+chunk_size]

def fake_get_for(response):
    return lambda *args, **kwargs: response

downloader = ns['_h15_download_installer_file']
payload = b'LimbusLyric verified installer fixture' * 200
sha = hashlib.sha256(payload).hexdigest()
base_candidate = {
    'installer_url':'https://downloads.example/LimbusLyric_Setup.exe',
    'installer_sha256':sha,
    'installer_name':'LimbusLyric_Setup_Test.exe',
    'installer_size':len(payload),
}
with tempfile.TemporaryDirectory() as td:
    path, size, actual = downloader(base_candidate, td, fake_get_for(FakeResponse(payload)))
    assert Path(path).read_bytes() == payload and size == len(payload) and actual == sha
    assert not Path(path + '.part').exists(), 'verified .part must be atomically consumed'

with tempfile.TemporaryDirectory() as td:
    bad_hash = dict(base_candidate, installer_sha256='0'*64)
    try:
        downloader(bad_hash, td, fake_get_for(FakeResponse(payload)))
        raise AssertionError('hash mismatch unexpectedly accepted')
    except RuntimeError as exc:
        assert 'SHA-256' in str(exc)
    assert not list(Path(td).glob('*.part')), 'hash mismatch left partial file behind'

with tempfile.TemporaryDirectory() as td:
    try:
        downloader(base_candidate, td, fake_get_for(FakeResponse(payload, url='http://downgrade.example/setup.exe')))
        raise AssertionError('non-HTTPS redirect unexpectedly accepted')
    except RuntimeError as exc:
        assert '非 HTTPS' in str(exc)

with tempfile.TemporaryDirectory() as td:
    huge = ns['H15_UPDATE_MAX_BYTES'] + 1
    try:
        downloader(base_candidate, td, fake_get_for(FakeResponse(b'', header_size=huge)))
        raise AssertionError('oversized response unexpectedly accepted')
    except RuntimeError as exc:
        assert '大小上限' in str(exc)

print('FRONTEND + VERIFIED INSTALLER UPDATE H15 REPLAY: PASS')
print('  R4 top navigation/search + runtime card scale baseline integration: PASS')
print('  current version derives from build tag; H/F ordering: PASS')
print('  GitHub/custom manifest HTTPS + SHA-256 installer contract: PASS')
print('  no digest / non-HTTPS => manual-only, never auto-execute: PASS')
print('  streamed downloader hash/redirect/size fault injection: PASS')
