#!/usr/bin/env python3
import ast
import html
import pathlib
import re
import sys


def fail(msg):
    print(f'UX SCRIPT + INSTRUMENTAL REPLAY: FAIL\n  - {msg}')
    raise SystemExit(1)

if len(sys.argv) != 2:
    print('usage: CHECK_UX_SCRIPT_INSTRUMENTAL_REPLAY.py <main.py>')
    raise SystemExit(2)

path = pathlib.Path(sys.argv[1])
src = path.read_text(encoding='utf-8')
try:
    tree = ast.parse(src)
except SyntaxError as exc:
    fail(f'main source does not parse: {exc}')

# Execute only the small pure-Python helpers under test.  This gate intentionally does not
# import the application module, so it remains runnable on release-audit machines without Qt.
want_assign = {
    'LATIN_VISUAL_CASCADE_ENABLED', 'HANGUL_VISUAL_CASCADE_ENABLED',
    'INSTRUMENTAL_CARD_HOLD_MS', 'SOFTWARE_TUTORIAL_URL',
    '_LRC_TIME_TOKEN_RE', '_LRC_INLINE_TIME_RE', '_LRC_OFFSET_RE',
    '_LRC_METADATA_ONLY_RE', '_LRC_CREDIT_BODY_RE', '_LRC_EXTRA_CREDIT_RE',
    '_LRC_CONTROL_RE', '_INSTRUMENTAL_BOILERPLATE_RE',
}
want_funcs = {
    '_token_cascade_candidate', '_lrc_fraction_ms', '_lrc_match_to_ms',
    '_split_lrc_leading_timestamps', '_sanitize_lrc_body',
    '_instrumental_boilerplate_bodies', '_instrumental_notice_compact', '_instrumental_notice_text_variants', '_instrumental_notice_strip_provider_meta', '_is_instrumental_boilerplate_payload', '_is_netease_sparse_instrumental_placeholder', '_provider_pure_music_flag', '_lyric_payload_profile', '_provider_payload_instrumental', '_build_lyric_payload_meta', '_is_primary_instrumental_payload', '_instrumental_track_card_lrc',
}
selected = []
for node in tree.body:
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        names = set()
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                names.add(target.id)
        if names & want_assign:
            selected.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in want_funcs:
        selected.append(node)

ns = {'re': re, 'html': html}
try:
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), ns, ns)
except Exception as exc:
    fail(f'cannot load pure helpers: {exc}')

cascade = ns.get('_token_cascade_candidate')
instrumental = ns.get('_is_instrumental_boilerplate_payload')
netease_sparse = ns.get('_is_netease_sparse_instrumental_placeholder')
pure_flag = ns.get('_provider_pure_music_flag')
profile = ns.get('_lyric_payload_profile')
payload_instrumental = ns.get('_provider_payload_instrumental')
build_payload_meta = ns.get('_build_lyric_payload_meta')
primary_instrumental = ns.get('_is_primary_instrumental_payload')
card = ns.get('_instrumental_track_card_lrc')
if not all(callable(x) for x in (cascade, instrumental, netease_sparse, pure_flag, profile, payload_instrumental, build_payload_meta, primary_instrumental, card)):
    fail('required pure helpers not found')

# Safe presentation-only cascade matrix.  Korean precomposed syllables are the new gap being
# closed.  Existing Latin/Greek/Cyrillic behavior must remain; shaping-dependent scripts stay atomic.
positive = [
    ('Hello', 'smart'),
    ('Καλημέρα', 'smart'),
    ('Привет', 'smart'),
    ('한글노래', 'smart'),
    ('대한민국', 'smart'),
]
negative = [
    ('中文歌词', 'smart'),
    ('かなカナ', 'smart'),
    ('العربية', 'smart'),
    ('עברית', 'smart'),
    ('ภาษาไทย', 'smart'),
    ('देवनागरी', 'smart'),
    ('한글', 'smart'),  # decomposed Hangul Jamo must not be split
    ('👨\u200d👩\u200d👧\u200d👦', 'smart'),
]
for text, effect in positive:
    if cascade(text, effect) is not True:
        fail(f'expected smart cascade for {text!r}')
for text, effect in negative:
    if cascade(text, effect) is not False:
        fail(f'unsafe/unintended smart cascade for {text!r}')
if cascade('한글', 'token'):
    fail('token mode must stay provider-atomic for Korean')
if not cascade('한글', 'typewriter'):
    fail('explicit typewriter should allow precomposed Korean syllables')
if cascade('ภาษาไทย', 'typewriter'):
    fail('explicit typewriter must not split Thai shaping')

# Provider instrumental boilerplate should become a compact title/artist card, while real lyric
# content that merely mentions pure music must remain lyric content.
notices = [
    '[00:00.00]此歌曲为没有填词的纯音乐，请您欣赏',
    '[00:00.00]纯音乐，请欣赏',
    '[00:00.00]Instrumental',
    '[ti:Example]\n[ar:Artist]\n[00:00.00]此歌曲为没有填词的纯音乐，请您欣赏',
    '[00:00.00]作曲：Someone\n[00:01.00]纯音乐，请欣赏',
    '[00:05.00]此歌曲暂无歌词，请欣赏',
    '[00:10.77]此歌曲\n[00:15.81]为没有\n[00:18.48]填词的\n[00:44.67]纯音乐\n[00:63.00]请欣赏',
    '[00:10.77]此歌曲\n[00:15.81]为没有\n[00:18.48]填词的\n[00:44.67]纯音乐\n[00:58.71]请\u200b欣赏',
    '[00:05.00]纯音乐，\u200b请欣赏',
    # Real KuGou V9 log shape: provider repeats the same marker on five timed rows.
    '[00:10.77]纯音乐\n[00:15.81]纯音乐\n[00:18.48]纯音乐\n[00:44.67]纯音乐\n[00:63.00]纯音乐',
    # Presentation-only reversible mojibake recovery; provider payload itself remains untouched.
    '[00:05.00]' + '纯音乐，请欣赏'.encode('utf-8').decode('latin1'),
    # Exact V11 runtime failure class: mojibake BOM means normal metadata cleanup misses
    # [id]/[qq:total], leaving those tokens in front of the repaired provider notice.
    ('\ufeff[id:00000000]\n[qq:total=320317]\n[00:01.58]纯音乐，请欣赏').encode('utf-8').decode('latin1'),
]
for payload in notices:
    if not instrumental(payload):
        fail(f'instrumental notice not recognized: {payload!r}')
real_lyrics = [
    '[00:00.00]我们听着纯音乐\n[00:03.00]继续向前走',
    '[00:00.00]Instrumental love\n[00:03.00]is not silent',
    '[00:00.00]纯音乐，请欣赏\n[00:05.00]但这一行是真歌词',
]
for payload in real_lyrics:
    if instrumental(payload):
        fail(f'legitimate lyric misclassified as instrumental: {payload!r}')
# Runtime NetEase V9 miss shape from the user's log: one short CJK row at 5s on a long track.
if not netease_sparse('[00:05.00]纯音乐，请欣赏', 101001):
    fail('NetEase sparse 1-row@5s pure-music placeholder not recognized')
if not netease_sparse('[00:05.00]此歌曲为纯音乐', 95381):
    fail('NetEase sparse 7-char 1-row@5s placeholder not recognized')
if netease_sparse('[00:05.00]hello', 101001):
    fail('NetEase sparse Latin one-line lyric was misclassified')
if netease_sparse('[00:25.00]山高水长', 101001):
    fail('NetEase arbitrary late sparse lyric was misclassified')

# Primary-source fast path: once the selected provider itself says this is instrumental,
# the quality ladder must not spend several seconds querying the other two providers.
if not primary_instrumental('酷狗', ('\ufeff[id:00000000]\n[qq:total=320317]\n[00:01.58]纯音乐，请欣赏').encode('utf-8').decode('latin1'), 189000):
    fail('KuGou mojibake+metadata primary notice not recognized for fast-path closure')
if not primary_instrumental('网易云', '[00:05.00]此歌曲为纯音乐', 95381):
    fail('NetEase sparse primary notice not recognized for fast-path closure')
if primary_instrumental('酷狗', '[00:00.00]我们听着纯音乐\n[00:03.00]继续向前走', 189000):
    fail('normal KuGou lyric incorrectly triggered primary instrumental fast path')

# V14: payload provenance survives cross-provider borrowing without changing transport identity.
if pure_flag({'pureMusic': True}) is not True or pure_flag({'pureMusic': 0}) is not False:
    fail('provider pureMusic flag coercion failed')
if pure_flag({'other': True}) is not None or pure_flag({'pureMusic': 'maybe'}) is not None:
    fail('unknown pureMusic values must stay unknown')
meta = build_payload_meta(
    {'source': 'QQ音乐'}, '网易云', '[00:05.00]纯音乐，请欣赏', 116165, {'pure_music_hint': True}
)
if meta.get('source') != 'QQ音乐' or meta.get('lyric_payload_source') != '网易云':
    fail('cross-provider payload provenance overwrote transport source')
if meta.get('lyric_payload_instrumental') is not True or meta.get('lyric_payload_rows') != 1:
    fail('cross-provider instrumental payload metadata missing')
if not payload_instrumental('网易云', '[00:05.00]纯音乐，请欣赏', 116165, {'pure_music_hint': True}):
    fail('borrowed NetEase instrumental payload was not recognized')
normal_meta = build_payload_meta(
    {'source': 'QQ音乐'}, '网易云', '[00:01.00]第一句歌词\n[00:05.00]第二句歌词', 116165, {'pure_music_hint': False}
)
if normal_meta.get('lyric_payload_instrumental'):
    fail('normal borrowed lyrics misclassified as instrumental')

render_card = card('如常', '草东没有派对')
if '如常' not in render_card or '草东没有派对' not in render_card:
    fail('instrumental card does not preserve title and artist')
if '纯音乐' in render_card or '请您欣赏' in render_card:
    fail('instrumental card leaked provider boilerplate')

if ns.get('SOFTWARE_TUTORIAL_URL') != 'https://space.bilibili.com/262118249?spm_id_from=333.1007.0.0':
    fail('software tutorial URL changed')
if int(ns.get('INSTRUMENTAL_CARD_HOLD_MS') or 0) < 15000:
    fail('instrumental card hold is unexpectedly short')

# Source-level wiring assertions for UI-only features and presentation isolation.
required_snippets = [
    "QDesktopServices.openUrl(QUrl(SOFTWARE_TUTORIAL_URL))",
    "self.tutorial_btn = QPushButton('软件教学')",
    "self.manage_font_btn = QPushButton('管理字体')",
    "class DiyStylePreview(QWidget)",
    "self.diy_font_reset_btn = QPushButton('恢复全局字体')",
    "self.diy_color_reset_btn = QPushButton('恢复全局颜色')",
    "self.diy_edge_reset_btn = QPushButton('边缘效果恢复全局')",
    "self.diy_motion_reset_btn = QPushButton('动效恢复全局')",
    "self.current_track_card = QFrame()",
    "self.instrumental_card_hold_spin = QSpinBox(self)",
    "self.provider_idle_tail_spin = QSpinBox(self)",
    "provider_idle_release_tail_ms",
    "self.lyric_window.set_track_card_mode(True, _instrumental_hold_ms)",
    "self.media_sync.set_lyric_click_timeline(click_timeline_text)",
    "纯音乐歌曲卡自动收尾",
    "媒体快照分项慢调用",
    "播放器读取慢调用",
]
for needle in required_snippets:
    if needle not in src:
        fail(f'missing wiring: {needle}')

# Instrumental substitution must happen in the renderer path only.  The original provider text is
# retained as click_timeline_text before the card replacement.
launch = None
for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == 'ControlPanel':
        launch = next((n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == '_launch_current_lyrics'), None)
        break
if launch is None:
    fail('ControlPanel._launch_current_lyrics missing')
launch_src = ast.get_source_segment(src, launch) or ''
if 'click_timeline_text = text' not in launch_src or '_instrumental_track_card_lrc' not in launch_src:
    fail('instrumental presentation isolation is not explicit in launch path')
if '纯音乐展示判定' not in launch_src or not any(m in launch_src for m in ('INSTRUMENTAL-RUNTIME-V18','INSTRUMENTAL-RUNTIME-V19','INSTRUMENTAL-RUNTIME-V20','INSTRUMENTAL-RUNTIME-V21','INSTRUMENTAL-RUNTIME-V22','INSTRUMENTAL-RUNTIME-V23','INSTRUMENTAL-RUNTIME-V24','INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')):
    fail('instrumental runtime-path diagnostic/version marker missing')
if 'primary_duration_safe = duration_compatible(provider_duration_ms, duration)' not in src or '_provider_payload_instrumental(source, primary_lrc, expected_ms, primary_meta)' not in src:
    fail('duration-safe primary instrumental fast-path classification missing from lyric quality ladder')
if "and not primary_instrumental" not in src or '纯音乐主源快速收口' not in src:
    fail('cross-provider instrumental fast-path short-circuit wiring missing')
for needle_v14 in (
    '酷狗新曲Range旧纪元仅作切歌提示',
    "source in ('QQ音乐', '酷狗')",
    '酷狗全局鼠标事件已快丢弃',
    'MediaSessionSync._kugou_poll_pointer_gesture = _limbus_kugou_poll_pointer_gesture_ui_safe',
    '纯音乐歌曲卡首锚前立即展示',
    'LyricWindow._playback_position = _limbus_track_card_playback_position',
    '酷狗同曲空歌手抖动已抑制',
    'ControlPanel._detected_player_track = _limbus_detected_player_track_stable',
    '跨平台纯音乐证据提前收口',
    '自动歌词来源切换补搜',
    '阻止新曲搜索期间重启旧歌词',
    'log_coalesced=1',
    "payload_source == '网易云'",
):
    if needle_v14 not in src:
        fail(f'V14 closure wiring missing: {needle_v14}')

print('UX SCRIPT + INSTRUMENTAL REPLAY: PASS')
print('  Korean precomposed syllables gain safe intra-token visual cascade: PASS')
print('  Latin/Greek/Cyrillic retained; shaping-sensitive scripts stay atomic: PASS')
print('  instrumental boilerplate -> title/artist card; real lyrics not hidden: PASS')
print('  tutorial/status/DIY preview/font-manager/reset wiring present: PASS')
print('  provider click-timeline text stays separate from instrumental render card: PASS')
print('  slow-call telemetry wiring present without authority assertions: PASS')
