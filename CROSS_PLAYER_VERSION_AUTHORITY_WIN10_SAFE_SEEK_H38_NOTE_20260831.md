# H38 — Cross-player version authority + Win10 safe seek

Field logs from H37P1 showed that Win10's frozen safety profile was correctly avoiding the in-process UIA/MSAA paths that had previously crashed through comtypes, but the fallback state machine still allowed lyric-provider duration to stand in for player duration. This made a correct physical KuGou rail geometry scale against an 81-second wrong same-title KRC. The same payload could then survive a KuGou → NetEase player switch even after NetEase native logs proved a 221.5-second playback item.

H38 makes duration authority explicit. On Win10 KuGou, provider/KRC duration is retained only as a presentation/search candidate and is not written into MediaSync or used as the user-seek scale until player-side evidence corroborates it. GSMTC timeline duration is accepted when available. When it is absent, H38 uses the already fail-closed physical rail detector to infer total duration from rail velocity: the motion ratio is independent of whatever candidate duration was used to express the observation. Several coherent estimates are required before promotion. No pywinauto/MSAA/comtypes path is re-enabled.

A player-owned duration that conflicts with the currently loaded same-title lyric version triggers a new search under the currently selected lyric source with that duration as the version constraint. Thus cross-provider lyrics remain supported, but title+artist alone no longer implies that two players are playing the same release/version.

Finally, a committed KuGou rail seek owns a 5.5-second same-identity transport window. Ambiguous GSMTC Media/Playback restart callbacks in that window cannot reset the local presentation clock to zero. Track changes remain outside this veto.
