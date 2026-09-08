# H42P2 release resume hotfix (2026-09-01)

Runtime behavior is unchanged from H42/H42P1. H42P2 adds a narrowly-scoped release-build resume path for the H29 gate-scope packaging failure observed after a complete 103/104 gate run.

`RESUME_AFTER_H29_GATE_FIX.cmd` is intentionally fail-closed. It only runs when the existing `.build_installer_venv_ascii` from the failed build is present. It reruns release metadata preflight, the changed H29 replay, the H42 field-safety replay, and the pinned runtime/import verification before continuing with PyInstaller, frozen smoke test, Inno Setup and portable packaging. It does not reinstall dependencies and does not rerun the unchanged first 103 release gates.

Normal releases must continue to use `BUILD_END_USER_INSTALLER.cmd`, which still runs the complete canonical suite.
