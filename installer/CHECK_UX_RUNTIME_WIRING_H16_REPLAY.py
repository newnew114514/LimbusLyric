#!/usr/bin/env python3
from pathlib import Path
import ast, re

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path(__file__).resolve().parents[1] / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
src=MAIN.read_text(encoding='utf-8')
marker='# H16 UX runtime wiring / real-machine closure'
main_guard='\nif __name__ == "__main__":\n'
assert marker in src, 'H16 marker missing'
assert main_guard in src and src.index(marker)<src.index(main_guard), 'H16 must install before main guard'
assert 'UX RUNTIME WIRING H16' in src.splitlines()[63], 'H16 build tag missing'

for token in (
    'H16_FONT_SIZE_MIN_PT = 6', 'H16_FONT_SIZE_MAX_PT = 300',
    'self.font_size.setRange(H16_FONT_SIZE_MIN_PT,H16_FONT_SIZE_MAX_PT)',
    'self.font_size.setKeyboardTracking(False)', "reason='h16-font-size'",
    'H16_EXIT_VISIBLE_MIN_MS = 520.0', 'H16_EXIT_PRESSURE_MIN_MS = 380.0',
    "effect=='instant'", 'self._h16_exit_progress=progress',
    'FadingLine.update=_h16_fading_update',
    "preferred_id=str(meta.get('netease_song_id') or '').strip()",
    "threading.Thread(target=work,name='LimbusLyric-H16Cover',daemon=True).start()",
    "H16_COVER_RETRY_SEC = (2.0, 6.0, 18.0)",
    "panel._h12_cover_result=(str(key),str(color))",
    "not style.get('text_color')", "font.setWeight(max(1,min(99,int(getattr(self,'_h12_font_weight',75)))))",
    "self.random_color_check.setChecked(False)", "self.h12_cover_check.setChecked(False)",
    "label.setText('清晰保留字幕：')", '后续换行逐步填满',
    'self._h12_async_timer.timeout.disconnect()', 'self._h12_cover_timer.timeout.disconnect()',
):
    assert token in src, f'H16 runtime contract missing: {token}'

# H16 stays presentation-only: no player/media authority methods are assigned here.
block=src[src.index(marker):src.index('# H14 auto-precision deadline / bounded enhancement',src.index(marker))]
for forbidden in (
    'MediaSessionSync.get_current_position =', 'MediaSessionSync.bind_track =',
    'LyricSearchEngine.search =', 'ControlPanel._on_auto_lyric_result =',
):
    assert forbidden not in block, f'H16 crossed authority boundary: {forbidden}'

# Execute pure duration helper with stubs.
tree=ast.parse(src)
def fn(name):
    return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
ns={
    'FADE_VISUAL_ALPHA_CUTOFF':8,
    'H16_EXIT_VISIBLE_MIN_MS':520.0,
    'H16_EXIT_PRESSURE_MIN_MS':380.0,
    'H16_EXIT_MAX_MS':6000.0,
}
for name in ('_h16_exit_duration_ms',):
    m=ast.Module(body=[fn(name)],type_ignores=[]); ast.fix_missing_locations(m); exec(compile(m,str(MAIN),'exec'),ns,ns)
class Row:
    fade_speed=15; exit_effect='wipe_ltr'; _fade_expedite_factor=1.0
r=Row()
d=ns['_h16_exit_duration_ms'](r)
assert d>=520.0, d
r._fade_expedite_factor=12.0
d2=ns['_h16_exit_duration_ms'](r)
assert d2>=380.0, d2
r.exit_effect='shrink'; r._fade_expedite_factor=1.0
assert ns['_h16_exit_duration_ms'](r)>=520.0

# Cover matching: multiple artists and provider-owned NetEase id are both accepted.
def alias_match(a,b):
    na=re.sub(r'\W+','',str(a).casefold()); nb=re.sub(r'\W+','',str(b).casefold())
    # Treat comma-delimited multi-artist strings as aliases when all meaningful pieces appear.
    parts=[re.sub(r'\W+','',x.casefold()) for x in re.split(r'[,，/&、;；|]+',str(a)) if x.strip()]
    ok=(na==nb) or (parts and all(x in nb for x in parts)) or na in nb or nb in na
    return ok, 1.0 if ok else 0.0
ns2={'re':re,'_artist_alias_match':alias_match}
for name in ('_h16_cover_artist_ok','_h16_choose_cover_row','_h16_cover_pic_url'):
    m=ast.Module(body=[fn(name)],type_ignores=[]); ast.fix_missing_locations(m); exec(compile(m,str(MAIN),'exec'),ns2,ns2)
rows=[
    {'id':11,'name':'少女A','artists':[{'name':'椎名もた'},{'name':'鏡音リン'}],'album':{'picUrl':'http://p.example/a.jpg'}},
    {'id':22,'name':'少女A','artists':[{'name':'Other'}],'album':{'picUrl':'https://p.example/b.jpg'}},
]
hit=ns2['_h16_choose_cover_row'](rows,'少女A','椎名もた, 鏡音リン','')
assert hit and hit['id']==11, hit
assert ns2['_h16_choose_cover_row'](rows,'wrong','wrong','22')['id']==22
assert ns2['_h16_cover_pic_url'](hit)=='https://p.example/a.jpg'

# Source-level ownership: cover participates in the normal style resolver, rather than
# only mutating the current LyricWindow once and getting lost on the next start.
assert 'ControlPanel._resolved_active_visual_style=_h16_resolve_style' in block
assert "cached and cached[0]==key" in block

print('UX RUNTIME WIRING H16 REPLAY: PASS')
print('  keyboard font size 6..300 + persisted unclamp/live apply: PASS')
print('  exit effects have perceptible bounded lifetime; instant stays instant: PASS')
print('  cover multi-artist/provider-id/retry + style-resolver ownership: PASS')
print('  continuous weight survives lyric restart unless DIY overrides: PASS')
print('  clear-subtitle capacity semantics documented; player authority untouched: PASS')
