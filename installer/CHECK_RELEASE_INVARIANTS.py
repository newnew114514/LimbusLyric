from __future__ import annotations
import re
import ast, sys
from pathlib import Path
from PACKAGING_PATH_POLICY import source_payload_path
if len(sys.argv)!=3:
    print("usage: CHECK_RELEASE_INVARIANTS.py <project-root> <main.py>"); raise SystemExit(2)
root=Path(sys.argv[1]).resolve(); main=Path(sys.argv[2]).resolve(); source=main.read_text(encoding="utf-8"); tree=ast.parse(source,filename=str(main)); fail=[]; notes=[]
SOURCE_VALUES={"网易云","QQ音乐","酷狗"}; PLAYER_VALUES={"网易云音乐","QQ音乐","酷狗音乐"}
def dotted(node):
    parts=[]
    while isinstance(node,ast.Attribute): parts.append(node.attr); node=node.value
    if isinstance(node,ast.Name): parts.append(node.id)
    return ".".join(reversed(parts))
def direct(body,scope="<module>"):
    seen={}
    for n in body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): seen.setdefault(n.name,[]).append(n.lineno)
    for name,lines in seen.items():
        if len(lines)>1: fail.append(f"duplicate definition in {scope}: {name} at {lines}")
    for n in body:
        if isinstance(n,ast.ClassDef): direct(n.body,scope+"."+n.name)
direct(tree.body)
for n in ast.walk(tree):
    if not isinstance(n,ast.Compare) or len(n.comparators)!=1: continue
    for call,lit in ((n.left,n.comparators[0]),(n.comparators[0],n.left)):
        if isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and call.func.attr=="currentText" and isinstance(call.func.value,ast.Attribute) and isinstance(lit,ast.Constant) and isinstance(lit.value,str):
            owner=dotted(call.func.value); value=lit.value
            if owner.endswith("source_combo") and value not in SOURCE_VALUES: fail.append(f"line {n.lineno}: source_combo impossible value {value!r}")
            if owner.endswith("player_combo") and value not in PLAYER_VALUES: fail.append(f"line {n.lineno}: player_combo impossible value {value!r}")
threads=0
for n in ast.walk(tree):
    if isinstance(n,ast.Call) and dotted(n.func)=="threading.Thread":
        threads+=1; kw={x.arg:x.value for x in n.keywords if x.arg}; d=kw.get("daemon")
        if not (isinstance(d,ast.Constant) and d.value is True): fail.append(f"line {n.lineno}: threading.Thread not daemon=True")
notes.append(f"threading.Thread daemon audit: {threads}")
classes={n.name:n for n in tree.body if isinstance(n,ast.ClassDef)}
def method(cls,name): return next((n for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
ms=classes.get("MediaSessionSync"); cp=classes.get("ControlPanel")
if not ms or not cp:
    fail.append("MediaSessionSync/ControlPanel missing")
else:
    if method(ms,"bind_track") is None:
        fail.append("MediaSessionSync.bind_track missing")
    cpstart=method(cp,"start"); cpstop=method(cp,"stop")
    if cpstart and "arm_kugou_manual_provisional" in ast.unparse(cpstart):
        fail.append("reverted KuGou manual arm returned in ControlPanel.start")
    if cpstop and "disarm_kugou_manual_provisional" in ast.unparse(cpstop):
        fail.append("reverted KuGou manual disarm returned in ControlPanel.stop")
    bind=method(ms,"bind_track"); bindsrc=ast.unparse(bind) if bind else ""
    if "_reset_kugou_provisional_state" in bindsrc:
        fail.append("reverted KuGou provisional reset returned in bind_track")
if "getattr(self, '_netease_native_last_track_serial', -1) or -1" in source: fail.append("track_serial zero collapses to -1")
if 'self.source_combo.currentText() == "酷狗音乐"' in source: fail.append("dead source_combo KuGou trigger remains")
if "pywin32==311" not in (root/"requirements_core.txt").read_text(encoding="utf-8"): fail.append("pywin32 must be 311")
for name in ("INSTALL_BRIDGE.cmd","LimbusLyricNCMBridge.plugin","UNINSTALL_BRIDGE.cmd"):
    if (root/name).exists(): fail.append("BetterNCM payload present: "+name)
opener=(root/"OPEN_LOG_FOLDER.cmd").read_text(encoding="utf-8",errors="ignore")
if r"%LOCALAPPDATA%\LimbusLyric\logs" not in opener: fail.append("OPEN_LOG_FOLDER does not use unified LOCALAPPDATA logs")
iss=(root/"installer"/"LimbusLyric_Setup.iss").read_text(encoding="utf-8-sig")
if "PrivilegesRequired=lowest" not in iss: fail.append("Inno not lowest privilege")
if "打开诊断日志" not in iss or r"{localappdata}\LimbusLyric\logs" not in iss: fail.append("Inno unified LOCALAPPDATA log shortcut missing")
if r'Name: "{localappdata}\LimbusLyric\logs"; Flags: uninsneveruninstall' not in iss: fail.append("Inno preserved LOCALAPPDATA logs dir missing")
if "LimbusLyric_Setup_1.8.9.136" not in iss: fail.append("Inno output not v1.8.9.136")
build=(root/"installer"/"BUILD_RELEASE.cmd").read_text(encoding="ascii",errors="ignore")
suite=(root/"installer"/"RELEASE_GATE_SUITE.tsv").read_text(encoding="utf-8",errors="ignore")
for token in ("LimbusLyric_Setup_1.8.9.136.exe","LimbusLyric_Portable_1.8.9.136.zip","--packaging-smoke-test","RUN_RELEASE_GATE_SUITE.py","CLEAN_PROJECT_PYTHON_CACHE.py","PYTHONDONTWRITEBYTECODE=1"):
    if token not in build: fail.append("BUILD_RELEASE missing "+token)
for token in ("CHECK_NO_VISIBLE_SUBPROCESSES.py","CHECK_RELEASE_INVARIANTS.py","CHECK_KUGOU_GOLDEN_BASELINE.py","CHECK_KUGOU_CAUSAL_CLOCK_GUARD_REPLAY.py","CHECK_KUGOU_PAUSE_RESUME_CAUSAL_BOOTSTRAP_REPLAY.py","CHECK_KUGOU_SEEK_SEED_RECOVERY_REPLAY.py","CHECK_LEGACY_BASELINE_INTEGRITY.py","CHECK_RC11_TARGETED_FIXES.py","CHECK_CODEX_PROTECTED_BEHAVIOR.py","CHECK_MAIN_SOURCE_LOCK.py","CHECK_QQ_SANDBOX_DUAL_CLOCK_REPLAY.py","CHECK_QQ_STARTUP_AUTHORITY_REPLAY.py","CHECK_QQ_LOOP_TRANSPORT_REPLAY.py","CHECK_QQ_TEXT_BOUNDARY_RANGE_FUSE_REPLAY.py","CHECK_RC_UI_HYGIENE_LOG5_REPLAY.py","CHECK_KUGOU_HOST_RAIL_REWORK_REPLAY.py","CHECK_GUI_HOTPATH_ISOLATION_REPLAY.py","CHECK_RUNTIME_FAULT_INJECTION_ABSENCE.py","CHECK_GUI_HOTPATH_FAULT_INJECTION_REPLAY.py","CHECK_POST_RELEASE_RESPONSIVENESS_H11_REPLAY.py","CHECK_RUNTIME_HARDENING_H17_REPLAY.py","CHECK_LYRIC_PIPELINE_V14_REPLAY.py","CHECK_LYRIC_PIPELINE_V16_SWITCH_INTRO_REPLAY.py","CHECK_LYRIC_PIPELINE_V17_NORMAL_DISPLAY_RESTORE_REPLAY.py","CHECK_KUGOU_WIN10_CRASH_HARDENING_H22_REPLAY.py"):
    if token not in suite: fail.append("RELEASE_GATE_SUITE missing "+token)
if re.search(r'%ROOT%\\installer\\CHECK_[A-Z0-9_]+\.py.*\|\| goto FAIL', build): fail.append("BUILD_RELEASE restored first-failure CHECK_* chain")
# RC9 KuGou golden-restore invariants.
if "paused_proven = [r for r in alive if r.get('pause_since') is not None" not in source:
    fail.append("KuGou golden pause-freeze proof missing")
if "continuous_proven = proof_age >= 12.5 and transport_status == 'playing'" not in source:
    fail.append("KuGou golden continuous-no-wrap proof missing")
if "'kugou-numeric-memory-cs', 'gsmtc-kugou-precise'" not in source:
    fail.append("KuGou numeric memory is no longer a golden strong clock source")
for forbidden in (
    "arm_kugou_manual_provisional",
    "disarm_kugou_manual_provisional",
    "_reset_kugou_provisional_state",
    "KUGOU_NUMERIC_PAUSE_PROOF_ENABLED",
    "KUGOU_NUMERIC_CONTINUOUS_PROOF_ENABLED",
    "KUGOU_NUMERIC_VALIDATOR_VERSION",
):
    if forbidden in source:
        fail.append("RC9 KuGou golden restore still contains reverted layer: "+forbidden)
# User-requested QQ compatibility restore: software-2 continuous-clock behavior wins.
# The two remaining request_urgent_scan(2.0) calls are unrelated legacy paths; the
# software-1 QQ press/release hooks must not be reintroduced.
qq_pointer = method(ms, "_qq_poll_pointer_gesture") if ms else None
qq_pointer_src = ast.unparse(qq_pointer) if qq_pointer else ""
if "request_urgent_scan(2.0)" in qq_pointer_src:
    fail.append("QQ software-1 progress press/release urgent-scan hooks returned")
for forbidden in (
    "QQ_UNARMED_GSMTC_VETO_MS",
    "qq-unarmed-gsmtc-veto",
    "QQ切歌隔离跨绑定保留",
    "qq-track-switch-fallback-hold",
    "trusted-fallback-blocked-during-active-track-switch-quarantine",
    "QQ自动歌词结果时长身份冲突丢弃",
    "qq_duration_identity_reject",
):
    if forbidden in source:
        fail.append("QQ software-1-only guard returned: "+forbidden)
if "click_fast = bool(now <= float(getattr(self, '_qq_nonrail_click_until_mono'" not in source:
    fail.append("QQ software-2 nonrail click-fast baseline missing")
# Audit only canonical project source. Build/runtime artifacts are excluded by
# the same policy used by the packaging-structure and cache-clean gates.
def is_project_source_path(p):
    return source_payload_path(root, p)
junk=[p for p in root.rglob("*") if p.is_file() and is_project_source_path(p) and (p.suffix.lower()==".pyc" or "__pycache__" in p.parts)]
if junk:
    preview=", ".join(str(p.relative_to(root)) for p in junk[:5])
    fail.append(f"project-source Python cache artifacts: {len(junk)} ({preview})")
pyfiles=sorted(p for p in root.rglob("*.py") if p.is_file() and is_project_source_path(p))
for p in pyfiles:
    try: compile(p.read_text(encoding="utf-8"),str(p),"exec")
    except Exception as e: fail.append(f"compile failed {p.relative_to(root)}: {e}")
notes.append(f"project python compile audit: {len(pyfiles)}")
if fail:
    print("RELEASE INVARIANT AUDIT: FAIL")
    for x in fail: print("  - "+x)
    raise SystemExit(23)
print("RELEASE INVARIANT AUDIT: PASS")
for x in notes: print("  "+x)
