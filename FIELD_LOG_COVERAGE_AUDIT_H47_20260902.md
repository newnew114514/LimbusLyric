# Field-log coverage audit — H47 — 2026-09-02

82 collected inputs reduce to 67 unique log sessions by SHA-256. Categories overlap. A missing
`日志会话结束` is not counted as a crash because older builds did not always emit that marker.

## Four priority logs

| Log | Evidence | Current coverage |
| --- | --- | --- |
| `155449_pid15640` | Session-end marker followed by native fatal `0x80010108`; no render pressure | H47 unhooks WH_MOUSE_LL, joins native/UIA/WinRT workers, then permits Qt teardown |
| `155224_pid11568` | Clean exit; paint max 17.6 ms, GUI stall max 47 ms, provider max 12 ms | Historical control; no fatal or hard-freeze evidence |
| `224208_pid7400` | Clean exit; unsafe one-row cross-provider lyric rejected by H41 | H41 completeness gate remains covered |
| `224438_pid2420` | Session end followed by `0x80010012`; 917 H30 warming logs | H47 closes late native teardown; H38 preserves a valid zero gesture baseline instead of resetting H30 each poll |

## Combined fixes

| Cluster | Sessions | Current status |
| --- | ---: | --- |
| Native fatal after session end | 2 | Root-cause fix + H47 replay; real-machine confirmation still required |
| Automatic-search transaction storm | 4 | Generation/stale-payload veto, H44 debounce, H46 in-flight Start preservation |
| H30 visual-wait storm | 3 | Zero-baseline reset fixed; H30/H38/H40/H41 replay coverage |
| KuGou synthetic-zero bootstrap | 5 | P4/H35 existing-playback guard |
| NetEase anonymous/sentinel clock and stale paused authority | newest field branch | H45 identity fail-closed + H46 trusted GSMTC anchor repair |
| Render/GUI high-water evidence | 25 | GUI isolation and H44 emergency lane mitigate the tail; hardware variability remains |
| Provider call >=100 ms | 10 | Kept off GUI hot paths; external latency remains variable |

## Honest release assessment

The known actionable failure clusters now have a direct guard and runnable replay. The remaining
uncertainty is environmental: logs and synthetic replay cannot prove COM, accessibility, graphics
drivers, or third-party player versions on every user machine. H47 improves the expected behavior
for the supplied evidence without claiming universal proof before affected-machine retest.

