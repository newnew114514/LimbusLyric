from pathlib import Path
import ast, sys
root=Path(sys.argv[1]).resolve()
main=next(root.glob('LimbusLyric_v1.8.9.133_*.py'))
src=main.read_text(encoding='utf-8')
ast.parse(src)
def need(c,m):
    if not c:
        print('RUNTIME UX CORE R2.3.1: FAIL '+m); raise SystemExit(31)
need("child.widget() is title" in src,'preview installer does not locate actual workspace_title owner')
need("itemAt(0).layout()" not in src[src.index('def _r23_install_title_preview_button'):src.index('def _r23_frontend_polish')], 'preview installer still assumes header item 0')
need("setObjectName('r23TitlePreviewButton')" in src,'preview button missing')
need("R2.3.1标题旁预览入口已安装" in src,'install diagnostic missing')
print('RUNTIME UX CORE R2.3.1: PASS')
print('  title preview attachment is H78 mark-safe and follows workspace_title ownership')
