#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, re, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_RENDER_HOTPATH_UI_COHERENCE_H95F7_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
marker='# H95F7 render hotpath + UI coherence'
need(marker in src,'H95F7 marker missing')
need('+ RENDER HOTPATH + UI COHERENCE H95F7' in src,'H95F7 build tag missing')
start=src.index(marker); end=src.index('# H95F8 lyric payload firewall + long-line containment + adaptive high-refresh',start); block=src[start:end]
for token in (
    'painter.drawPixmapFragments(fragments,sheet)',
    '_hires_glyph_sprite(',
    'window._schedule_song_fragment_atlas(visual_style=visual_style,prewarm_only=True)',
    "globals()['_h95f5_translation_for_line']=lambda *_a,**_k: ''",
    "row._h95f5_translation=''",
    'H95F7_EDGE_GUARD_PX = 14',
    "layout.takeAt(i)",
    "frame.frameShape()==QFrame.HLine",
    "panel.h95f6_bilingual_check.setEnabled(True)",
    "bar.setProperty('h95f6ModernGlass',False)",
    "bar.setProperty('h95f7ModernGlass',bool(modern))",
    'H95F7_DEAD_SLOW_VERIFY_MS = 10000.0',
): need(token in block,'H95F7 integration missing: '+token)
# No provider/transport-clock takeover. Liveness worker scheduling is the single deliberate
# MediaSessionSync surface and may not touch clock/seek methods.
for bad in ('LyricSearchEngine.search =','parse_lrc =','MediaSessionSync.position','MediaSessionSync.seek','_playback_position ='):
    need(bad not in block,'H95F7 crossed authority boundary: '+bad)

funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
def fn(name): need(name in funcs,'function missing: '+name); return funcs[name]
def segment(name): return ast.get_source_segment(src,fn(name)) or ''
# The exact regression: active/history translation hot draw must never rebuild vector text.
for name in ('_h95f7_draw_active_translation','_h95f7_draw_history_translation'):
    seg=segment(name)
    need('QPainterPath' not in seg and '.addText(' not in seg,name+' rebuilt vector glyphs in hot path')
    need('drawPixmapFragments' in seg and '_h95f7_sprite_for' in seg,name+' lacks atlas batch + sprite fallback')

# Execute the real liveness scheduling policy.
lns={'PLAYER_LIVENESS_POLL_MS':550.0,'H95F7_ALIVE_POLL_MS':1500.0,'H95F7_DEAD_FAST_POLL_MS':1500.0,'H95F7_DEAD_SLOW_VERIFY_MS':10000.0}
exec(compile(ast.Module(body=[fn('_h95f7_liveness_poll_plan')],type_ignores=[]),'<h95f7-live>','exec'),lns)
plan=lns['_h95f7_liveness_poll_plan']
need(plan(None,1000,0)==('full',550.0),'unknown liveness cadence changed')
need(plan(True,1000,0)==('fast-then-full-on-miss',1500.0),'alive fast cadence missing')
need(plan(False,9000,5000)==('fast-only',1500.0),'dead process still runs expensive probe every poll')
need(plan(False,16000,5000)==('full',1500.0),'dead slow verification never returns')

# Execute symmetric language reconciliation with fakes. Unlike H95F6, trans-only must not
# disable the bilingual target; a user can click straight from either mode to the other.
class Check:
    def __init__(self,on=False): self.on=bool(on); self.enabled=True; self.block=False
    def isChecked(self): return self.on
    def setChecked(self,v): self.on=bool(v)
    def setEnabled(self,v): self.enabled=bool(v)
    def blockSignals(self,v): self.block=bool(v)
class W:
    def __init__(self): self.enabled=True
    def setEnabled(self,v): self.enabled=bool(v)
class P:
    def __init__(self):
        self._h95f5_bilingual_mode='bilingual'; self.trans_check=Check(True); self.h95f6_bilingual_check=Check(True); self.h95f6_translation_scale=W(); self.h95f6_translation_gap=W(); self.h95f6_translation_scale_label=W()
def set_bilingual(panel,on,save=True):
    panel._h95f5_bilingual_mode='bilingual' if on else 'original'; panel.h95f6_bilingual_check.setChecked(on)
language_ns={'_h95f5_norm_mode':lambda v:'bilingual' if str(v)=='bilingual' else 'original','_h95f6_set_bilingual':set_bilingual}
exec(compile(ast.Module(body=[fn('_h95f7_sync_language_controls')],type_ignores=[]),'<h95f7-lang>','exec'),language_ns)
panel=P(); language_ns['_h95f7_sync_language_controls'](panel)
need(panel._h95f5_bilingual_mode=='original' and not panel.h95f6_bilingual_check.isChecked(),'trans-only did not evict bilingual mode')
need(panel.h95f6_bilingual_check.enabled is True,'bilingual target is still disabled by trans-only')
panel.trans_check.on=False; panel._h95f5_bilingual_mode='bilingual'; language_ns['_h95f7_sync_language_controls'](panel)
need(panel.h95f6_bilingual_check.isChecked() and panel.h95f6_translation_scale.enabled,'bilingual mode cannot be re-entered directly')

# Atlas charset wrapper executes against the real AST: secondary styles must union translated
# chars while the primary style key remains untouched.
class Win:
    def _fragment_style_signature_for_visual(self,visual): return ('style',str(visual))
def pre(win,visual=None): return (['A'],(('primary',),'mainkey'))
atlas_ns={'_H95F7_CHARS_KEY_PRE':pre,'_h95f7_translation_chars':lambda w:['译','A'],'hashlib':__import__('hashlib')}
exec(compile(ast.Module(body=[fn('_h95f7_song_fragment_chars_and_key')],type_ignores=[]),'<h95f7-atlas>','exec'),atlas_ns)
chars,key=atlas_ns['_h95f7_song_fragment_chars_and_key'](Win(),('font','color','glow'))
need(chars==['A','译'] and key[0][0]=='style','translation chars were not joined into secondary atlas')
chars0,key0=atlas_ns['_h95f7_song_fragment_chars_and_key'](Win(),None)
need(chars0==['A'] and key0==(('primary',),'mainkey'),'primary atlas was unnecessarily enlarged')

# Execute sync-card compaction with layout fakes. Hidden retired widgets are not enough:
# their four QHBoxLayout rows and the old H95 divider must leave the VBox entirely.
class FakeItem:
    def __init__(self,widget=None,layout=None): self._widget=widget; self._layout=layout
    def widget(self): return self._widget
    def layout(self): return self._layout
class FakeLayout:
    def __init__(self,items=None): self.items=list(items or [])
    def count(self): return len(self.items)
    def itemAt(self,i): return self.items[i]
    def takeAt(self,i): return self.items.pop(i)
    def removeWidget(self,w): self.items=[it for it in self.items if it.widget() is not w]
    def insertWidget(self,i,w): self.removeWidget(w); self.items.insert(i,FakeItem(widget=w))
class FakeQFrame:
    HLine=7
    def __init__(self,shape=0): self.shape=shape; self.hidden=False
    def frameShape(self): return self.shape
    def hide(self): self.hidden=True
class FakeLabel:
    def __init__(self): self.text=''
    def setText(self,v): self.text=str(v)
class FakeCard(FakeQFrame):
    def __init__(self,layout,frames): super().__init__(0); self._layout=layout; self.frames=frames
    def layout(self): return self._layout
    def findChildren(self,_cls): return list(self.frames)
class FakePanel: pass
proxies=[object() for _ in range(4)]
retired=[FakeLayout([FakeItem(widget=w)]) for w in proxies]
output_row=FakeLayout([FakeItem(widget=object())])
divider=FakeQFrame(FakeQFrame.HLine); inspector=FakeQFrame(0); hint=FakeLabel()
main_layout=FakeLayout([FakeItem(widget=object()),FakeItem(widget=hint)]+[FakeItem(layout=r) for r in retired]+[FakeItem(layout=output_row),FakeItem(widget=divider),FakeItem(widget=inspector)])
card=FakeCard(main_layout,[divider,inspector]); panel2=FakePanel(); panel2.h75_sync_output_card=card; panel2.h75_offset_proxies={str(i):w for i,w in enumerate(proxies)}; panel2.h95f6_player_inspector=inspector; panel2.h95f6_player_hint=hint
compact_ns={'QFrame':FakeQFrame}
exec(compile(ast.Module(body=[fn('_h95f7_compact_sync_output')],type_ignores=[]),'<h95f7-sync-ui>','exec'),compact_ns)
need(compact_ns['_h95f7_compact_sync_output'](panel2) is True,'sync output compaction did not execute')
need(all(not (it.layout() in retired) for it in main_layout.items),'retired player offset rows still occupy VBox geometry')
need(divider.hidden and all(it.widget() is not divider for it in main_layout.items),'obsolete H95 divider still occupies/paints the card')
need(main_layout.itemAt(2).widget() is inspector,'current-player inspector was not moved into compact position')

# Modern glass stays translucent and is explicitly modern-only.
m1=re.search(r'h95f7ModernGlass="true"\]\[h95f4Palette="classic"\].*?rgba\(10,10,13,(\d+)\)',block,re.S)
m2=re.search(r'h95f7ModernGlass="true"\]\[h95f4Palette="studio"\].*?rgba\(12,18,17,(\d+)\)',block,re.S)
need(m1 and m2,'H95F7 glass QSS missing')
need(105<=int(m1.group(1))<=130 and 105<=int(m2.group(1))<=130,'modern title glass is outside the requested 40-50% black range')

# Compact sync cleanup must remove the retired layout items, not merely hide their widgets.
seg=segment('_h95f7_compact_sync_output')
need('layout.takeAt(i)' in seg,'retired player rows still reserve VBox height')
need("frame.frameShape()==QFrame.HLine" in seg,'obsolete divider cleanup missing')

print('RENDER HOTPATH + UI COHERENCE H95F7 REPLAY: PASS')
print('  secondary atlas + cached sprite hotpath: PASS')
print('  no per-frame QPainterPath.addText in translation lane: PASS')
print('  dead-player liveness CPU backoff: PASS')
print('  bidirectional translation/bilingual switching: PASS')
print('  compact sync layout + modern glass scope: PASS')
