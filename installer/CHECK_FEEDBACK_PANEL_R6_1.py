#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
main = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
src = main.read_text(encoding='utf-8-sig')

def need(token, message):
    if token not in src:
        print('FEEDBACK PANEL R6.1: FAIL')
        print(' - ' + message)
        raise SystemExit(61)

need("FEEDBACK_EMAIL = '1826555940@qq.com'", 'feedback email changed/missing')
need('def _feedback_template_text(self):', 'copyable feedback template missing')
need('def _show_feedback_dialog(self):', 'in-app feedback dialog missing')
need("self.feedback_btn.clicked.connect(self._show_feedback_dialog)", 'feedback button still bypasses in-app dialog')
need("copy_email_btn = QPushButton('复制邮箱')", 'copy-email action missing')
need("copy_info_btn = QPushButton('复制反馈信息')", 'copy-feedback action missing')
need("log_btn = QPushButton('打开日志目录')", 'open-log action missing')
need("mail_btn = QPushButton('打开邮件应用（可选）')", 'optional mail action missing')
need("QApplication.clipboard().setText(FEEDBACK_EMAIL)", 'email clipboard path missing')
need("QApplication.clipboard().setText(text)", 'feedback-template clipboard path missing')
need("mail_btn.clicked.connect(self._open_feedback_email)", 'mailto must remain optional inside dialog')
need("self.feedback_btn.setToolTip(f'打开本地反馈面板", 'feedback tooltip must describe local/no-browser path')
# The primary button must not directly invoke mailto/browser anymore.
if 'self.feedback_btn.clicked.connect(self._open_feedback_email)' in src:
    print('FEEDBACK PANEL R6.1: FAIL')
    print(' - primary feedback button still directly invokes mailto')
    raise SystemExit(62)
print('FEEDBACK PANEL R6.1: PASS')
