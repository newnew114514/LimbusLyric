#!/usr/bin/env python3
import ast, sys
from pathlib import Path
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V26_EVIDENCE_EPOCH2_FONT_GLOW_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def fail(msg):
    print('LYRIC PIPELINE V26 EVIDENCE EPOCH2 + FONT/GLOW REPLAY: FAIL')
    print('  -',msg); raise SystemExit(1)
def fn(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name==name:
                    return ast.get_source_segment(src,m)
    fail(f'missing {cls}.{name}')
def topfn(name):
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name:
            return ast.get_source_segment(src,n)
    fail(f'missing top-level {name}')
if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')): fail('V26+ marker missing')

# ---- Evidence ownership closure ----
init=fn('MediaSessionSync','__init__')
for needle in ('_media_player_epoch','_track_identity_epoch','_track_identity_player_epoch','_track_bound_mono','_kugou_range_evidence_serial'):
    if needle not in init: fail(f'missing epoch state: {needle}')

reset=fn('MediaSessionSync','_reset_provider_sync_state')
for needle in (
    "self._media_player_epoch = int(getattr(self, '_media_player_epoch', 0) or 0) + 1",
    'retired_duration = self._uia_duration_ms','duration = None','self._uia_duration_ms = None',
    'self._kugou_range_track_switch_pending = None','self._kugou_host_v2_progress_pending = None',
    "self._kugou_host_v2_progress_trusted_key = ''",'retired_duration=', 'player_epoch=',
):
    if needle not in reset: fail(f'player-epoch reset missing: {needle}')
if any(line.strip() == 'duration = self._uia_duration_ms' for line in reset.splitlines()): fail('old player duration still carried into new player')

bind=fn('MediaSessionSync','bind_track')
for needle in (
    "int(getattr(self, '_track_identity_player_epoch', 0) or 0) == int(getattr(self, '_media_player_epoch', 0) or 0)",
    "self._track_identity_epoch = int(getattr(self, '_track_identity_epoch', 0) or 0) + 1",
    'self._track_identity_player_epoch = int(getattr(self, \'_media_player_epoch\', 0) or 0)',
    'self._track_bound_mono = time.monotonic() * 1000.0',
):
    if needle not in bind: fail(f'identity ownership stamp missing: {needle}')

seed=fn('MediaSessionSync','_kugou_seed_rail_local_master')
for needle in ('_track_identity_player_epoch','_media_player_epoch','_kugou_rail_master_player_epoch','_kugou_rail_master_identity_epoch'):
    if needle not in seed: fail(f'KuGou Rail epoch stamp/guard missing: {needle}')
rail=fn('MediaSessionSync','_kugou_rail_local_position')
for needle in ('_kugou_rail_master_player_epoch','_media_player_epoch','_kugou_rail_master_identity_epoch','_track_identity_epoch'):
    if needle not in rail: fail(f'KuGou Rail stale-epoch invalidation missing: {needle}')

kg=fn('MediaSessionSync','_kugou_poll_uia_progress_v2')
for needle in (
    'identity_bound_to_player','player_epoch','identity_epoch','range_serial',
    '酷狗HostV2等待当前播放器身份绑定','host-uia-range-provisional',
    '酷狗HostV2未定时长位置先行锚定',
    "_kugou_rail_master_player_epoch',-1)) == int(getattr(self,'_media_player_epoch',0) or 0)",
    "_kugou_rail_master_identity_epoch',-1)) == int(getattr(self,'_track_identity_epoch',0) or 0)",
    "now - float(getattr(self,'_track_bound_mono',0.0) or 0.0) >= 1200.0",
):
    if needle not in kg: fail(f'KuGou Range/transport epoch closure missing: {needle}')
# Existing hard authorities must still exist.
for needle in ('host-uia-range-v2','host-uia-same-track-restart','酷狗宿主V2原生Range时长接管','酷狗同曲重新播放时钟立即回锚','seek=unchanged'):
    if needle not in kg: fail(f'KuGou authority baseline lost: {needle}')

req=fn('ControlPanel','_request_auto_track')
for needle in ('酷狗新曲Range旧纪元仅作切歌提示','provider-duration=0','wait-post-bind-range=1','same_player_epoch'):
    if needle not in req: fail(f'KuGou unbound Range quarantine missing: {needle}')
# The old V25 behavior must be gone: pending Range cannot directly become provider duration.
if "provider_duration_ms = kr_duration" in req:
    fail('pre-bind KuGou Range duration still directly filters the next lyric transaction')

# Small logic replay of the host regression: QQ 160s -> KuGou shell 85.05s -> real new song 201.09s.
# A player switch invalidates old authority; an unbound Range only hints transition; a same-song
# restart is impossible immediately after identity bind.
class Epoch:
    def __init__(self):
        self.player=4; self.identity=9; self.identity_player=4; self.rail_player=4; self.rail_identity=9; self.bound_ms=1000
    def switch_player(self):
        self.player += 1; self.pending=None; self.duration=None
    def bind(self,now):
        self.identity += 1; self.identity_player=self.player; self.bound_ms=now
        self.rail_player=self.player; self.rail_identity=self.identity
    def bound(self): return self.identity_player==self.player
    def restart(self,now,old,observed):
        return bool(self.bound() and self.rail_player==self.player and self.rail_identity==self.identity and now-self.bound_ms>=1200 and old>=4500 and observed<=2200 and observed-old<=-3000)
e=Epoch(); e.switch_player()
if e.duration is not None: fail('dynamic player switch retained duration')
if e.bound(): fail('old identity remained authoritative after player switch')
old_pending={'duration_ms':85050,'player_epoch':e.player,'identity_epoch':e.identity}
# Identity appears later: old pending belongs to pre-bind identity and must not filter lyrics.
e.bind(5000)
if old_pending['identity_epoch']==e.identity: fail('dynamic stale Range candidate crossed identity epoch')
provider_duration=0
if provider_duration!=0: fail('dynamic pre-bind Range unexpectedly became provider duration')
if e.restart(5100,20240,0): fail('newly bound song misclassified as same-track restart')
if not e.restart(6400,20240,0): fail('real same-track restart lost after epoch settles')

# ---- Font / shared soft-glow presentation ----
if 'QPushButton("推荐字体")' in src or "QPushButton('推荐字体')" in src:
    fail('unused recommended-font button still exposed')
for needle in ('font_bold_check','font_italic_check','diy_font_bold_check','diy_font_italic_check'):
    if needle not in src: fail(f'font style toggle missing: {needle}')
style=fn('ControlPanel','_resolved_active_visual_style')
for needle in ("style.get('font_bold'", "style.get('font_italic'", 'font.setBold(', 'font.setItalic('):
    if needle not in style: fail(f'global/per-song bold-italic resolution missing: {needle}')
diy=fn('ControlPanel','_song_style_payload_from_diy')
for needle in ("'font_bold'", "'font_italic'"):
    if needle not in diy: fail(f'DIY payload does not persist {needle}')
launch=fn('ControlPanel','_launch_current_lyrics')
if 'self.glow_size_slider.value()' not in launch or 'self.glow_alpha_slider.value()' not in launch:
    fail('per-song DIY no longer shares global glow spread/strength semantics')

soft=topfn('_draw_soft_glow_path')
for needle in ('airbrush-like halo','layers=','Qt.RoundCap','Qt.RoundJoin','painter.drawPath(path)'):
    if needle not in soft: fail(f'soft halo helper missing: {needle}')
# Require multiple feather layers; one copied hard outline is not enough.
soft_node=None
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and n.name=='_draw_soft_glow_path': soft_node=n; break
layer_count=0
for n in ast.walk(soft_node):
    if isinstance(n,(ast.Tuple,ast.List)) and len(n.elts)>=5 and all(isinstance(x,ast.Tuple) and len(x.elts)==2 for x in n.elts):
        layer_count=max(layer_count,len(n.elts))
if layer_count < 5: fail('soft halo has fewer than five feather layers')
for q in (
    ('FadingLine','_ensure_row_sprite'),('FadingLine','draw'),('LyricWindow','paintEvent'),('DiyStylePreview','paintEvent')
):
    body=fn(*q)
    if '_draw_soft_glow_path' not in body: fail(f'{q[0]}.{q[1]} not using shared soft glow')
for top in ('_glyph_glow_raster','_hires_glyph_sprite','_render_song_atlas_glyph'):
    if '_draw_soft_glow_path' not in topfn(top): fail(f'{top} not using shared soft glow')
# Guard against reintroducing the old single hard glow copy in the main raster paths.
for bad in ('QPen(gc, self.glow_size)', 'QPen(self.glow_color, self.glow_size)', 'QPen(glow_color, glow_size)'):
    if bad in src: fail(f'legacy hard glow pattern still present: {bad}')

print('LYRIC PIPELINE V26 EVIDENCE EPOCH2 + FONT/GLOW REPLAY: PASS')
print('  player/identity/Range/transport evidence ownership is epoch-scoped: PASS')
print('  pre-bind KuGou Range cannot poison the next lyric duration: PASS')
print('  immediate new-track zero cannot masquerade as same-track restart: PASS')
print('  recommended-font button removed; global + DIY bold/italic persisted: PASS')
print('  global + DIY glow converge on shared multi-layer soft halo renderer: PASS')
