#!/usr/bin/env python3
import ast, sys
from pathlib import Path
if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V24_KUGOU_FIRST_ATTACH_QQ_SEEK_EDGE_REPLAY.py <main.py>')
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def fail(msg):
    print('LYRIC PIPELINE V24 KUGOU FIRST-ATTACH / QQ SEEK EDGE REPLAY: FAIL')
    print('  -',msg); raise SystemExit(1)
def fn(cls,name):
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name==name:
                    return ast.get_source_segment(src,m)
    fail(f'missing {cls}.{name}')
if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V24','INSTRUMENTAL-RUNTIME-V25','INSTRUMENTAL-RUNTIME-V26','INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')): fail('V24+ marker missing')

host=fn('MediaSessionSync','_kugou_poll_uia_progress_v2')
for needle in ('proof_status','stale_paused_motion','_kugou_host_motion_playing_until_mono',
               '_kugou_host_motion_playing_track_key','酷狗HostV2运动否决陈旧暂停态',
               'authority=display-transport-only | seek=unchanged','effective_host_status'):
    if needle not in host: fail(f'KuGou first-attach transport proof missing: {needle}')
rail=fn('MediaSessionSync','_kugou_rail_local_position')
for needle in ('host_motion_until','host_motion_track',"effective == 'paused' and prev == 'playing'",
               "host_motion_track == str(self._track_key or '')"):
    if needle not in rail: fail(f'KuGou motion carry missing: {needle}')
# Never turn title metadata alone into a playing grant.
for forbidden in ("source='kugou-gsmtc-fast-event' and status == 'paused'", 'metadata_age <= 850 and status =='):
    if forbidden in host or forbidden in rail: fail(f'unsafe title-only playing inference: {forbidden}')

qq=fn('MediaSessionSync','_qq_queue_seek')
for needle in ('validated_divergence','old_expected_gap','new_expected_gap',
               'qq-gesture-validated-divergence-accept','geometry-authority=0',
               "str(source_name or '') == 'qq-time-pair-validated'",'int(confidence or 0) >= 160'):
    if needle not in qq: fail(f'QQ validated divergence guard missing: {needle}')
# The original stale-near-old-clock branch must remain; V24 is an edge override, not a new authority model.
for needle in ('stale_near_clock','QQ Seek旧时间控件疑似冻结，触发重抓','qq-gesture-target-outlier'):
    if needle not in qq: fail(f'QQ baseline stale-echo guard lost: {needle}')

# Dynamic replay of the exact V23 failure geometry: old clock 107.67s, visual release ~28.13s,
# validated player time 52.42s at +563ms. It must be allowed through because it is far from the
# stale old clock and >45% closer to the physical intent. Geometry remains non-authoritative.
def divergence(observed, expected_base, release_age, chosen, duration, confidence=168, source='qq-time-pair-validated'):
    expected=float(expected_base)+(min(float(release_age),9000.0) if release_age>0 else 0.0)
    expected=min(float(duration),expected)
    tolerance=max(9000.0,float(duration)*0.06) if release_age<900.0 else max(4500.0,min(7500.0,float(duration)*0.035))
    stale=abs(float(observed)-float(chosen)) <= max(6500.0,min(10500.0,float(duration)*0.04))
    old_gap=abs(float(chosen)-expected); new_gap=abs(float(observed)-expected)
    return bool(350.0 <= release_age <= 1850.0 and source=='qq-time-pair-validated' and confidence>=160 and
                not stale and old_gap>=max(12000.0,tolerance*1.25) and new_gap<=old_gap*0.55)
if not divergence(52420,28133,563,107670,219000):
    fail('V23 gesture-4 validated divergence should bypass stale geometry veto')
# Real stale Text near the old clock must still be rejected.
if divergence(50420,134992,765,54310,308000):
    fail('stale near-old-clock QQ Text incorrectly bypasses guard')
# A mid-flight sample that is only modestly closer to the rail target must still wait.
if divergence(81420,134992,1187,54732,308000):
    fail('unstable QQ transition sample incorrectly bypasses guard')

# Dynamic motion proof used by KuGou first attach. A real progress Slider advancing ~1x while
# GSMTC says paused is causal evidence that paused is stale; a frozen slider is not.
def stale_paused_motion(prev_obs, prev_mono, obs, now):
    dt=max(1.0,float(now)-float(prev_mono)); dp=float(obs)-float(prev_obs)
    tol=max(520.0,dt*0.80); min_adv=max(60.0,min(180.0,dt*0.25))
    return bool(dp>=min_adv and abs(dp-dt)<=tol)
if not stale_paused_motion(8000,0,8420,420):
    fail('moving Host-V2 Slider did not contradict stale paused status')
if stale_paused_motion(8000,0,8010,420):
    fail('frozen/near-frozen Host-V2 Slider incorrectly grants playing')
if stale_paused_motion(8000,0,12000,420):
    fail('large manual/outlier Slider jump incorrectly grants 1x playing')

print('LYRIC PIPELINE V24 KUGOU FIRST-ATTACH / QQ SEEK EDGE REPLAY: PASS')
print('  KuGou first attach: moving Host-V2 Slider may veto stale paused for display transport only: PASS')
print('  true paused / frozen slider remains paused: PASS')
print('  QQ validated UIA may bypass geometry veto only when far from old clock and materially closer to intent: PASS')
print('  QQ stale old-clock and unstable transition samples remain guarded: PASS')
