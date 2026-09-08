LimbusLyric Audited RC11 — H36 Installer + Portable
2026-08-31

运行：
    BUILD_END_USER_INSTALLER.cmd

预期输出：
    installer\release\LimbusLyric_Setup_1.8.9.134.exe
    installer\release\LimbusLyric_Portable_1.8.9.134.zip

目标机不需要 Python，也不需要 BetterNCM。
网易云 Native detector 默认启用。
日志优先写到 LimbusLyric.exe 同目录\logs。

构建保护：
- visible subprocess / CREATE_NO_WINDOW audit
- release invariants
- KuGou old-working golden baseline
- 481 个旧工作版未改函数完整性锁
- RC11 QQ targeted fix source lock + synthetic regression
- exact main-source lock
- pywin32/MFC/Qt/WinRT/cloudmusic_detector import check
- frozen LimbusLyric.exe --packaging-smoke-test
- H36 KuGou visual-authority / NetEase bootstrap closure
- canonical release gate coverage: 140 registered checks
