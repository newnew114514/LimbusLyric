#!/usr/bin/env python3
import ast, html, re, sys
from pathlib import Path
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V18_KUGOU_TEXT_SEAMLESS_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def fail(msg):
    print('LYRIC PIPELINE V18 KUGOU TEXT + SEAMLESS PRECISION REPLAY: FAIL'); print('  -',msg); raise SystemExit(1)
def fn(cls,name):
    for node in tree.body:
        if isinstance(node,ast.ClassDef) and node.name==cls:
            for item in node.body:
                if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)) and item.name==name:
                    return ast.get_source_segment(src,item)
    fail(f'missing {cls}.{name}')
def top_fn(name):
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return ast.get_source_segment(src,node)
    fail(f'missing {name}')
if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V18','INSTRUMENTAL-RUNTIME-V19','INSTRUMENTAL-RUNTIME-V20','INSTRUMENTAL-RUNTIME-V21','INSTRUMENTAL-RUNTIME-V22','INSTRUMENTAL-RUNTIME-V23','INSTRUMENTAL-RUNTIME-V24','INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')): fail('V18+ behavior marker missing')
# Real KuGou payload repair must happen before _clean_lrc, not only pure-music classification.
search=fn('LyricSearchEngine','search')
for n in ('repair_kugou_payload', "payload_source or '') == '酷狗'", '酷狗歌词正文可逆乱码修复', 'timing=preserved'):
    if n not in search: fail(f'KuGou payload repair missing: {n}')
if search.index('酷狗歌词正文可逆乱码修复') > search.index('clean_lrc = LyricSearchEngine._clean_lrc'):
    fail('KuGou mojibake repair occurs after generic LRC cleanup')
# Test the standalone repair rule with a real UTF-8-as-Latin1 style row.
helper=top_fn('_kugou_payload_text_repair')
ns={'html':html, '_LRC_TIME_TOKEN_RE':re.compile(r'\[(?:\d{1,3}:\d{1,2}(?:[.:]\d{1,3})?|\d{1,9})(?:\]|,)')}
exec(helper,ns)
repair=ns['_kugou_payload_text_repair']
original='\ufeff[00:00.00]山海\n[00:03.58]我看见一座山'
raw=original.encode('utf-8').decode('latin1')
out,changed,codec=repair(raw)
if not changed or '山海' not in out or '我看见一座山' not in out: fail(f'mojibake sample not repaired: {out!r}')
if len(re.findall(r'\[\d{1,3}:\d{1,2}',raw)) != len(re.findall(r'\[\d{1,3}:\d{1,2}',out)):
    fail('repair changed timed-row count')
# Same-track precise upgrade must not restart/clear visual stack.
up=fn('LyricWindow','upgrade_lyric_timeline_preserve_visual')
for n in ('visual_preserved','self.lyric_timeline = timeline','self.displayed_line_index = target'):
    if n not in up: fail(f'seamless timeline swap missing: {n}')
for forbidden in ('self.stop_lyric()', 'self.fading_lines = []', 'self.history_lines = []'):
    if forbidden in up: fail(f'seamless upgrade clears visual state: {forbidden}')
on=fn('ControlPanel','_on_auto_lyric_result')
for n in ('upgrade_lyric_timeline_preserve_visual','自动歌词精确升级无闪断接管','visual-reset=0','style-restart=0'):
    if n not in on: fail(f'ControlPanel seamless precision route missing: {n}')
# Pure music remains presentation-only and KuGou low-level clock methods remain untouched by this feature.
launch=fn('ControlPanel','_launch_current_lyrics')
if 'INSTRUMENTAL_CARD_HOLD_MS' not in launch or not any(m in launch for m in ('纯音乐歌曲卡柔和入场','纯音乐歌曲卡沿用用户入场效果')): fail('pure-music card regressed')
for name in ('_kugou_poll_pointer_gesture','_kugou_commit_gesture_seek'):
    body=fn('MediaSessionSync',name)
    if '乱码修复' in body or '无闪断' in body: fail(f'low-level KuGou method polluted: {name}')
print('LYRIC PIPELINE V18 KUGOU TEXT + SEAMLESS PRECISION REPLAY: PASS')
print(f'  reversible KuGou mojibake repaired with {codec}->utf8 while timed-row count stayed stable: PASS')
print('  same-track ordinary->precise upgrade preserves current/history/fading visuals: PASS')
print('  pure-music presentation and low-level KuGou clock/seek remain isolated: PASS')
