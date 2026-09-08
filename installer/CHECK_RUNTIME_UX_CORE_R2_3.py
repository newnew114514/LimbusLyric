from pathlib import Path
import ast, hashlib, sys

root=Path(sys.argv[1]).resolve()
main=next(root.glob('LimbusLyric_v1.8.9.133_*.py'))
src=main.read_text(encoding='utf-8')
tree=ast.parse(src)

def need(cond,msg):
    if not cond:
        print('RUNTIME UX CORE R2.3: FAIL '+msg)
        raise SystemExit(31)

def assign_rhs(target):
    out=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.Assign): continue
        for t in node.targets:
            if isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name):
                key=f'{t.value.id}.{t.attr}'
                if key==target:
                    try: out.append(ast.unparse(node.value))
                    except Exception: out.append(type(node.value).__name__)
    return out

# Historical frontend/runtime install topology must not change.
expected={
    'ControlPanel.__init__':54,
    'LyricWindow.paintEvent':10,
    'FadingLine.draw':17,
    'LyricWindow._make_history_line':18,
    'LyricSearchEngine.search':5,
    'MediaSessionSync.bind_track':6,
    'MediaSessionSync.snapshot':4,
}
for key,count in expected.items():
    need(len(assign_rhs(key))==count,f'{key} wrapper count {len(assign_rhs(key))}!={count}')

# Title-adjacent preview: zero layout cost folded; compact fixed host only when requested.
for token in (
    "setObjectName('r23TitlePreviewButton')",
    "btn.setText('收起预览' if opened else '预览')",
    "host.setMinimumHeight(0); host.setMaximumHeight(0); host.hide()",
    "host.setMinimumHeight(int(R23_PREVIEW_HOST_H)); host.setMaximumHeight(int(R23_PREVIEW_HOST_H)); host.show()",
    "R23_PREVIEW_HOST_H = 142",
    "legacy",
): need(token in src,'missing preview contract: '+token)
need("_h80_sync_studio_stage = _r23_sync_title_preview" in src,'H80 tab callback not routed to title preview')
need("_h95f4f3_sync_studio_stage = _r23_sync_title_preview" in src,'H95F4F3 callback not routed to title preview')

# Region map is inline/compact and the old 126px reservation is physically removed from layout.
for token in (
    'class R23RegionMiniPreview',
    'R23_REGION_MINI_W = 118',
    'R23_REGION_MINI_H = 48',
    'card.layout().removeWidget(old)',
    'panel.r22_region_preview = mini',
    '右侧小屏幕会实时显示结果',
): need(token in src,'missing compact region contract: '+token)

# Most-used visual controls move first and preset no longer owns its own card.
need("'字体与轮廓', '光与材质', '基础表现', '排版与布局', '字幕可出现范围'" in src,'appearance order is not frequent-first')
need("preset.setMinimumHeight(0); preset.setMaximumHeight(0); preset.hide()" in src,'standalone preset card not retired')
need("dst.insertLayout(insert_at, item.layout())" in src,'preset row not merged into font card')

# Additive sampledAt/capability contract inspired by external-player APIs; no authority takeover.
playback=(root/'limbus_core'/'playback_model.py').read_text(encoding='utf-8')
for token in (
    'class PlaybackCapabilities',
    'def position_at(self, mono_ms',
    'def sampled_dict(self, mono_ms',
): need(token in playback,'missing playback core contract: '+token)
need('MediaSessionSync.sampled_snapshot = _s2_playback_sampled_contract' in src,'sampled snapshot not published')
need('MediaSessionSync.capability_snapshot = _s2_capability_contract' in src,'capability snapshot not published')

# Unified lyric model derives grapheme and render hints once; visual consumers reuse them.
lyrics=(root/'limbus_core'/'lyric_model.py').read_text(encoding='utf-8')
for token in (
    'def build_line_render_hints',
    'def active_line_window',
    '"render_hints": render_hints',
): need(token in lyrics,'missing lyric core contract: '+token)
need("hints = shadow.get('render_hints')" in src,'H95F10F12 does not reuse unified render hints')

# Functional pure-core checks (no Qt/Win32/network).
sys.path.insert(0,str(root))
from limbus_core import PlaybackSnapshot, PlaybackCapabilities, build_unified_track_from_timeline, active_line_window
snap=PlaybackSnapshot.from_legacy({'connected':True,'status':'playing','position_ms':1000,'duration_ms':10000,'playback_rate':1.0},captured_mono_ms=5000.0)
need(snap.position_at(5750.0)==1750,'sampledAt extrapolation wrong')
need(snap.sampled_dict(6000.0)['sampled_position_ms']==2000,'sampled dict wrong')
cap=PlaybackCapabilities.from_mapping({'player':'kgmusic','uia_position':1,'local_holdover':1,'selected_clock':'host-uia-range-v2','transport_generation':3})
need(cap.uia_position and cap.local_holdover and cap.transport_generation==3,'capability normalization wrong')
track=build_unified_track_from_timeline([(1000,'AB',[(1000,1,1200,0),(1200,2,1500,1)]),(2000,'C',None)],song='x')
need(track['lines'][0]['render_hints']['handoff_ms']==2000,'render hint handoff wrong')
need(track['grapheme_event_count']==2,'grapheme timing count wrong')
win=active_line_window(track,1500,history=2,lookahead=2)
need(win['current_index']==0 and len(win['upcoming'])==1,'active lyric window wrong')

print('RUNTIME UX CORE R2.3: PASS')
print('  title-adjacent fixed preview is zero-height when folded')
print('  region explainer is inline 118x48 instead of a full empty row')
print('  preset row is merged into font/outline; frequent controls lead the page')
print('  sampledAt/capability playback contract is additive only')
print('  unified render hints feed the H95F10F12 plan contract; active_line_window remains a staged core API')
