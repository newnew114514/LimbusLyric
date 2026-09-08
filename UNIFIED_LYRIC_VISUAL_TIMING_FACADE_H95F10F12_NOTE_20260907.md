# H95F10F12 — Unified Lyric + Visual Timing Facade

- Reuses the existing H95 unified lyric shadow model; no second parser/model is introduced.
- Exposes a read-only provider-neutral lyric facade to RenderPlan.
- Rejects stale shadow rows when their main text disagrees with the mature live timeline.
- Names stable visual timing semantics: birth, content begin/end, handoff, semantic end.
- Main word timing is retained when the coherent H95 row contains provider word events; translation remains line-level.
- Does not change provider/search/player clock/seek or any mature entrance/exit/blur formula.
