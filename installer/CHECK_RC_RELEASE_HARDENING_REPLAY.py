#!/usr/bin/env python3
import ast
import json
import os
import sys
import tempfile
from pathlib import Path

if len(sys.argv) < 3:
    print('usage: CHECK_RC_RELEASE_HARDENING_REPLAY.py <root> <main.py>')
    raise SystemExit(2)
root = Path(sys.argv[1])
main = Path(sys.argv[2])
s = main.read_text(encoding='utf-8')

def need(cond, msg):
    if not cond:
        print('FAIL', msg)
        raise SystemExit(1)
    print('PASS', msg)

need('RC DIY ALL + PER-PLAYER + CUSTOM FONT + UX POLISH + HANGUL + INSTRUMENTAL 20260817' in s, 'current RC hardening build tag')
need('CONFIG_SCHEMA_VERSION = 5' in s, 'explicit config schema v5')
need("'schema_version': CONFIG_SCHEMA_VERSION" in s, 'config saves schema version')
need("'frontend_mode'" in s and "'margin_time'" in s, 'retired-key migration list retained')
need('用户配置版本迁移' in s and '_write_config_dict_atomic(data)' in s, 'atomic config migration wiring')
need('_LOG_KEEP_RECENT = 5' in s and '_LOG_MAX_SESSIONS = 5' in s, 'exact five-session retention')
need('_LOG_MAX_SESSION_BYTES = 12 * 1024 * 1024' in s, 'per-session log ceiling')
need('config_schema=' in s and 'log_policy=keep' in s, 'support environment fingerprint')
need('大多数情况下无需修改高级设置' in s, 'advanced settings user guidance')
need('恢复透视默认值' in s and 'def _reset_perspective_defaults' in s, 'perspective reset remains user-facing')
need("('空间透视', '按自己的观感调整立体透视，不影响歌词同步。', 6)" in s, 'advanced perspective card row count')
need('self.persp_x_slider.setValue(5)' in s and 'self.persp_y_slider.setValue(30)' in s and 'self.persp_comp_slider.setValue(3)' in s, 'perspective reset defaults')
need('PASS bundled-app-icon' in s and 'PASS config-root-writable' in s and 'PASS preferred-log-root' in s, 'frozen packaging smoke hardened')

# Verify retired pacing keys are no longer persisted as current user settings/presets.
tree = ast.parse(s)
funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
for fn_name in ('save_all_config',):
    fn = funcs[fn_name]
    text = ast.get_source_segment(s, fn) or ''
    need("'margin_time': panel.margin_spin.value()" not in text, f'{fn_name} does not persist margin_time')
    need("'max_interval': panel.max_interval_spin.value()" not in text, f'{fn_name} does not persist max_interval')
    need("'max_duration': panel.max_duration_spin.value()" not in text, f'{fn_name} does not persist max_duration')

cp = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_capture_style_preset')
cp_text = ast.get_source_segment(s, cp) or ''
need("'margin_time'" not in cp_text and "'max_interval'" not in cp_text and "'max_duration'" not in cp_text,
     'style presets no longer capture retired pacing knobs')
lp = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'load_preset')
lp_text = ast.get_source_segment(s, lp) or ''
need("('margin_time'," not in lp_text and "('max_interval'," not in lp_text and "('max_duration'," not in lp_text,
     'style presets no longer restore retired pacing knobs')

# Perspective remains persisted and preset-capable.
need("'persp_x_strength': panel.persp_x_slider.value()" in s and "'persp_y_strength': panel.persp_y_slider.value()" in s and "'persp_compensation': panel.persp_comp_slider.value()" in s,
     'perspective settings still persist')
need("('persp_x_strength', self.persp_x_slider, 'value')" in s and "('persp_y_strength', self.persp_y_slider, 'value')" in s,
     'perspective settings still restore from presets')


# Exercise config migration in isolation without importing the full PyQt/Windows application.
def top_fn_source(name):
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(s, node) or ''

with tempfile.TemporaryDirectory() as td:
    cfg = Path(td) / 'lyric_config.json'
    cfg.write_text(json.dumps({
        'settings': {
            'persp_x_strength': 17, 'qq_sync_offset': 33,
            'frontend_mode': 'sidebar', 'loop': False, 'ui_theme': 'limbus_manager',
            'margin_time': 999, 'max_interval': 1234, 'max_duration': 4567,
        },
        'presets': {'MyPreset': {'text': '#ffffff', 'persp_y_strength': 44, 'margin_time': 777}},
        'players': {'QQ音乐': {'process': 'QQMusic.exe'}},
        'song_styles': {'x|y': {'song': 'X', 'artist': 'Y', 'mode': 'all', 'rules': {'all': {'font_family': 'A'}, 'qq': {'font_family': 'Q'}}}},
    }, ensure_ascii=False), encoding='utf-8')
    logs = []
    ns = {
        'os': os, 'json': json, 'CONFIG_FILE': str(cfg), 'CONFIG_SCHEMA_VERSION': 5,
        '_RETIRED_SETTING_KEYS': frozenset({'frontend_mode','simplified_mode','simple_mode','compact_mode','loop','loop_protection','margin_time','max_interval','max_duration','ui_theme'}),
        '_RETIRED_PRESET_KEYS': frozenset({'margin_time','max_interval','max_duration'}),
        'DEFAULT_PRESETS': {'通用': {'text': '#fffeef'}},
        'DEFAULT_PLAYERS': {'网易云音乐': {'process': 'cloudmusic.exe'}, 'QQ音乐': {'process': 'QQMusic.exe'}, '酷狗音乐': {'process': 'kgmusic.exe'}},
        '_migrate_legacy_config_once': lambda: None,
        'write_error_log': lambda *a, **kw: logs.append((a, kw)),
    }
    exec(top_fn_source('_write_config_dict_atomic'), ns)
    exec(top_fn_source('load_all_config'), ns)
    migrated = ns['load_all_config']()
    need(migrated.get('schema_version') == 5, 'config migration writes schema v5')
    need(migrated['settings'].get('persp_x_strength') == 17 and migrated['settings'].get('qq_sync_offset') == 33,
         'config migration preserves visual/sync preferences')
    need(not any(k in migrated['settings'] for k in ('frontend_mode','loop','margin_time','max_interval','max_duration','ui_theme')),
         'config migration removes retired settings/theme selector')
    need(migrated['presets']['MyPreset'].get('persp_y_strength') == 44 and 'margin_time' not in migrated['presets']['MyPreset'],
         'config migration preserves preset visuals and removes retired pacing')
    need(all(name in migrated['players'] for name in ('网易云音乐','QQ音乐','酷狗音乐')),
         'config migration repairs built-in player profiles')
    style_row = migrated['song_styles']['x|y']
    need(style_row.get('mode') == 'all' and style_row.get('rules', {}).get('all', {}).get('font_family') == 'A' and style_row.get('rules', {}).get('qq', {}).get('font_family') == 'Q',
         'config migration preserves first-class ALL mode and existing provider payloads')
    disk = json.loads(cfg.read_text(encoding='utf-8'))
    need(disk.get('schema_version') == 5 and 'margin_time' not in disk.get('settings', {}),
         'config migration persists atomically')

print('RC RELEASE HARDENING REPLAY: PASS')
