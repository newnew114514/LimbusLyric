from pathlib import Path
import ast, sys
root=Path(sys.argv[1]).resolve()
main=next(root.glob('LimbusLyric_v1.8.9.133_*.py'))
src=main.read_text(encoding='utf-8')
tree=ast.parse(src)

def need(cond,msg):
    if not cond:
        print('VISIBILITY CLOCK SAFETY R2.4: FAIL '+msg)
        raise SystemExit(31)

def fn(name):
    return next((n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)

def segment(node):
    lines=src.splitlines()
    return '\n'.join(lines[node.lineno-1:node.end_lineno]) if node else ''

req=fn('_request_auto_track'); bind=fn('bind_track'); check=fn('check_lyric_time'); rescue=fn('request_visibility_clock_rescue')
need(req is not None,'_request_auto_track missing')
need(bind is not None,'MediaSessionSync.bind_track missing')
need(check is not None,'LyricWindow.check_lyric_time missing')
need(rescue is not None,'request_visibility_clock_rescue missing')
rs=segment(req); bs=segment(bind); cs=segment(check); xs=segment(rescue)

# The first-attach flag must be consumed by the first confirmed track transaction itself,
# not by a provider-specific lyric result branch. This is the regression that made later
# tracks repeatedly look like a startup late attach after R2.1 fast-stage acceptance.
need("R2.4首附着事务已消费" in rs,'first attach is not consumed in track request transaction')
need(rs.find('self.media_sync.bind_track(') < rs.find("R2.4首附着事务已消费") < rs.find("job = {"),
     'first attach consumption is not after bind and before async lyric job publication')
need("self._zero_touch_first_attach_pending = False" in rs,'persistent first-attach flag is not cleared')

# Cross-player startup rule: a true pre-existing song must never receive a fake zero clock.
need("if startup_existing:" in bs and "self._reset_auto_local_clock()" in bs,
     'startup-existing auto-local suppression missing')
need("elif _auto_proc == 'kgmusic'" in bs,'KuGou-specific local master branch lost')

# Visibility is a renderer fact now, not a search/container fact.
need('R2.4歌词已就绪但尚无可见字幕' in cs,'no-position visibility failure telemetry missing')
need('visual_count=0 | success=0' in cs,'visibility failure is not explicitly marked unsuccessful')
need('R2.4首条弹幕真正可见' in cs,'true first visible row commit telemetry missing')
need('visual_count>=1 | success=1' in cs,'true visibility success contract missing')
need('H34酷狗切歌自动弹幕显示已确认' not in src,'misleading H34 display-confirmed log still exists')
need('H34酷狗切歌弹幕容器已就绪' in src,'H34 container-ready replacement missing')

# Rescue is common but player-capability-specific; no generic fake authority.
for token in ("proc == 'kgmusic'", "proc in ('qqmusic', 'cloudmusic', 'spotify')",
              'kugou-host-backoff-reset', 'uia-urgent', 'display-local',
              'startup_existing', 'authority=display-only-or-existing-evidence | seek=unchanged'):
    need(token in xs,f'rescue contract missing: {token}')
need('_limbus_kugou_host_next_probe_mono = 0.0' in xs,'KuGou Host-V2 negative-cache rescue missing')
need('request_urgent_scan(2.5)' in xs,'async urgent evidence wakeup missing')

# Preserve runtime wrapper installation topology: this patch changes owners internally only.
def count_attr_assign(owner,attr):
    n=0
    for node in ast.walk(tree):
        if not isinstance(node,ast.Assign): continue
        for t in node.targets:
            if isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id==owner and t.attr==attr:
                n+=1
    return n
for owner,attr,count in (
    ('ControlPanel','__init__',54),('LyricWindow','paintEvent',10),('FadingLine','draw',17),
    ('LyricWindow','_make_history_line',18),('LyricSearchEngine','search',5),
    ('MediaSessionSync','bind_track',6),('MediaSessionSync','snapshot',4)):
    need(count_attr_assign(owner,attr)==count,f'{owner}.{attr} topology changed')

print('VISIBILITY CLOCK SAFETY R2.4: PASS')
print('  first-attach lifecycle is track-owned and provider-independent')
print('  startup-existing synthetic zero is forbidden for all players')
print('  visibility success requires a renderer row commit')
print('  QQ/KuGou/NetEase/Spotify rescue paths are capability-scoped')
