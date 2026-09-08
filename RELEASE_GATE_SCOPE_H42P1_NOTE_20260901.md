# H42P1 Release Gate Scope Fix — 2026-09-01

H42 runtime is unchanged. The H29 replay previously sliced source from the H29 marker all the way to the module `__main__` block. H42 legitimately added a later, independent bounded PSAPI helper containing `EnumProcesses`, so the historical assertion `EnumProcesses not in h29` falsely attributed H42 code to H29 and blocked packaging on Windows.

H42P1 narrows the replay slice to the actual H29 layer, ending at the H30 marker. The semantic H29 requirement remains unchanged: H29's NetEase cached-PID positive liveness path must not use full-system EnumProcesses or tasklist.

No production Python runtime code changed.
