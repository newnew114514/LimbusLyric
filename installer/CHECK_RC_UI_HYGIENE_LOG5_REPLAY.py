from pathlib import Path
import ast, os, sys, tempfile, time, threading

if len(sys.argv) != 2:
    print('usage: CHECK_RC_UI_HYGIENE_LOG5_REPLAY.py <main.py>')
    raise SystemExit(2)
path = Path(sys.argv[1])
source = path.read_text(encoding='utf-8')
fail=[]
def need(token, desc=None):
    if token not in source: fail.append(desc or f'missing: {token}')
def forbid(token, desc=None):
    if token in source: fail.append(desc or f'should be absent: {token}')

need('RC DIY ALL + PER-PLAYER + CUSTOM FONT + UX POLISH + HANGUL + INSTRUMENTAL 20260817', 'current DIY ALL/per-player UX build tag missing')
# Old engineering knobs are compatibility constants only, not public rows.
forbid('QLabel("留白：")', 'legacy 留白 row still visible')
forbid('QLabel("长间隔阈值：")', 'legacy 长间隔阈值 row still visible')
forbid('QLabel("长间隔时长：")', 'legacy 长间隔时长 row still visible')
need('self.margin_spin.setRange(4000, 4000)')
need('self.max_interval_spin.setRange(16000, 16000)')
need('self.max_duration_spin.setRange(5000, 5000)')
need('self.margin_spin.hide()'); need('self.max_interval_spin.hide()'); need('self.max_duration_spin.hide()')
forbid('QPushButton("重新校准")', 'manual recalibration button still public')
forbid('self.source_support_hint =', 'provider-specific support hint widget still public')

# User-facing visual preferences MUST remain adjustable and persisted.
for token in (
    'QCheckBox("立体透视")', 'QLabel("透视 X（左右）：")', 'QLabel("透视 Y（上下）：")',
    'QLabel("水平补偿：")', 'self.persp_x_slider.setRange(0, 100)',
    'self.persp_y_slider.setRange(0, 100)', 'self.persp_comp_slider.setRange(0, 100)',
    "settings.get('persp_x_strength', 5)", "settings.get('persp_y_strength', 30)",
    "settings.get('persp_compensation', 3)", "'persp_x_strength': self.persp_x_slider.value()",
    "'persp_y_strength': self.persp_y_slider.value()", "'persp_compensation': self.persp_comp_slider.value()",
): need(token)

# Public wording is product language; provider internals remain in diagnostics only.
need('QLabel("诊断日志最多保留 5 份；反馈问题时附上最近日志即可。")')
need('QPushButton("打开日志目录")')
need('QCheckBox("字幕越界后从另一侧回流")')
need('QCheckBox("音乐节奏字效")')
need('QLabel("歌词时间微调：")')
need('"不拆分（按歌词原有单位）"')
forbid('QCheckBox("音频响应字符（实验）")')
forbid('"原始 token（兼容）"')
need('source_suffix = "；逐字歌词"')
need('source_suffix = "；普通行歌词"')

# Log pool contract.
need('_LOG_KEEP_RECENT = 5')
need('_LOG_MAX_SESSIONS = 5')
need('_LOG_MAX_SESSION_BYTES = 12 * 1024 * 1024')
need('_LOG_SESSION_TRIM_TO_BYTES = 8 * 1024 * 1024')
need('_LOG_RETENTION_DAYS = 0')
need("write_error_log('运行环境', detail=_runtime_environment_detail(app), force_sync=True)")
need("self.status.setText(\"状态：已打开日志目录\")")
# LOCALAPPDATA must be the first real directory candidate.
fn_start = source.index('def _log_directory_candidates():')
fn_end = source.index('\ndef _choose_log_directory()', fn_start)
logdir_seg = source[fn_start:fn_end]
if logdir_seg.find("LOCALAPPDATA") < 0 or logdir_seg.find("app_dir") < 0 or logdir_seg.find("LOCALAPPDATA") > logdir_seg.find("app_dir"):
    fail.append('LOCALAPPDATA is not preferred before app_dir')
# Current session must exist before count cleanup.
fn_start = source.index('def _ensure_log_session():')
fn_end = source.index('\ndef _trim_log_file_if_needed', fn_start)
ensure_seg = source[fn_start:fn_end]
if ensure_seg.find('_LOG_SESSION_PATH = path') > ensure_seg.find('_cleanup_old_log_sessions'):
    fail.append('log cleanup still happens before current session is counted')

# Dynamically exercise the two maintenance helpers in isolation.
tree=ast.parse(source, filename=str(path))
def node_source(name):
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name:
            return ast.get_source_segment(source,n)
    raise KeyError(name)
ns={'os':os,'time':time,'_LOG_KEEP_RECENT':5,'_LOG_MAX_SESSIONS':5,
    '_LOG_MAX_TOTAL_BYTES':64*1024*1024,'_LOG_RETENTION_DAYS':0,
    '_LOG_MAX_SESSION_BYTES':2048,'_LOG_SESSION_TRIM_TO_BYTES':1024}
exec(node_source('_cleanup_old_log_sessions'),ns)
exec(node_source('_trim_log_file_if_needed'),ns)
with tempfile.TemporaryDirectory() as td:
    now=time.time()
    for i in range(7):
        p=Path(td)/f'LimbusLyric_20260101-00000{i}_pid{i}.log'
        p.write_text(f'log{i}\n',encoding='utf-8')
        os.utime(p,(now+i,now+i))
    ns['_cleanup_old_log_sessions'](td, now=now+100)
    rows=sorted(Path(td).glob('LimbusLyric_*.log'), key=lambda p:p.stat().st_mtime, reverse=True)
    if len(rows)!=5: fail.append(f'count cleanup kept {len(rows)} logs instead of 5')
    if rows and rows[0].name!='LimbusLyric_20260101-000006_pid6.log': fail.append('count cleanup did not preserve newest log')
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'LimbusLyric_long.log'
    p.write_text(''.join(f'{i:04d} abcdefghijklmnopqrstuvwxyz\n' for i in range(200)),encoding='utf-8')
    before=p.stat().st_size
    ns['_trim_log_file_if_needed'](str(p))
    after=p.stat().st_size
    text=p.read_text(encoding='utf-8')
    if not (after < before and after < 1500): fail.append(f'long session trim ineffective: before={before} after={after}')
    if not text.startswith('[log-maintenance] older diagnostics trimmed;'): fail.append('trim marker missing')

if fail:
    print('RC UI HYGIENE + LOG5 REPLAY: FAIL')
    for x in fail: print('  - '+x)
    raise SystemExit(30)
print('RC UI HYGIENE + LOG5 REPLAY: PASS')
