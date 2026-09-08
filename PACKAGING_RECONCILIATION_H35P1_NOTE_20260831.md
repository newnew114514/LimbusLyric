# H35P1 Packaging Reconciliation — 2026-08-31

This patch keeps the H35 runtime fixes unchanged and reconciles the source-package / build metadata workflow that repeatedly caused otherwise reviewed builds to fail before dependency installation.

## Root cause closed

`SHA256_FILES.txt` previously had to be hand-edited every time a new Hxx note or replay gate was added. `CHECK_PACKAGING_STRUCTURE.py` correctly treated any omission as fatal, so a valid source tree could fail at preflight simply because the source manifest was not regenerated after adding files.

## New packaging contract

- `CHECK_MAIN_SOURCE_LOCK.py` remains the first trust anchor and is not auto-repaired.
- `CHECK_RELEASE_GATE_COVERAGE.py` requires every `installer/CHECK_*.py` file to be registered exactly once in `RELEASE_GATE_SUITE.tsv` with a valid arg mode.
- `SYNC_SOURCE_MANIFEST_ADDITIONS.py` may auto-enrol only a registered new `CHECK_*.py` replay and root NOTE/AUDIT documents. Unknown new payload remains fatal.
- `RELEASE_GATE_SUITE.tsv` is treated as derived registration metadata: its SHA entry may refresh automatically only after its declarations exactly match all `CHECK_*.py` files.
- Existing hashes for normal source/build/spec/check files are never silently refreshed by one-click build preflight.
- `PREPARE_SOURCE_MANIFEST.py` is the maintainer-only deterministic full refresh path. It requires the main source lock and gate coverage to pass first.
- `CHECK_PACKAGING_CONTRACT.py` now locks PyInstaller semantics rather than the exact bytes of the `.spec` file, so harmless comments/formatting do not create a fake packaging regression.
- `CHECK_SOURCE_MANIFEST_AUTOSYNC_REPLAY.py` covers the previously failing Hxx add-note/add-gate scenario, suite-hash refresh, unknown-file rejection, and existing-hash tamper rejection.

The goal is not to make packaging permissive. It is to eliminate duplicated metadata bookkeeping while retaining strict failures for actual source drift, unregistered gates, cache pollution, duplicate project roots, unknown files, and runtime packaging changes.
