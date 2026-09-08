# RC Precision Ladder + QQ Background Display Audit — 2026-08-17

## Evidence addressed

- QQ hidden/background case: lyrics could finish loading while QQ UIA exposed no usable window/time pair and GSMTC had no numeric timeline, leaving the renderer with no display clock for the rest of a track.
- NetEase `烂尾楼`: NetEase supplied ordinary LRC (224571 ms), while a manually selected KuGou source supplied a valid precise KRC version (~223000 ms). The old provider-local enhancement path rejected the foreign candidate before common quality arbitration.

## Reviewed behavior

### Precise mode

Retrieval quality order is now:

1. selected provider precise lyric;
2. verified foreign precise lyric;
3. selected provider ordinary line LRC;
4. safe foreign ordinary line LRC.

Foreign precise timing must still pass track identity/duration guards and, when selected-provider ordinary LRC exists, content/timeline verification. The selected player's provider identity and duration remain authoritative; foreign provider IDs never bind transport identity.

### Classic mode

Classic mode is ordinary-only at retrieval time, not merely at rendering time. Separate ordinary helpers are used for NetEase / QQ / KuGou, with no YRC/KLYRIC/QRC/KRC word-timing probes. Inline enhanced-LRC time tags are stripped defensively. Precise/classic mode is part of the automatic lyric cache key so the two modes cannot reuse each other's retrieval payload.

The three protected provider search methods (`search_netease`, `search_qq`, `search_kugou`) remain source-identical to the prior reviewed candidate.

### QQ hidden-window display clock

A new display-only fallback can expose the existing local monotonic auto-track clock when:

- the current transport is QQ;
- the auto-track bootstrap is active and the lyric duration is known;
- source-affine QQ media metadata matches the bound track;
- the detected initial age is still plausible;
- the track is playing when the fallback first engages.

It does not write UIA/GSMTC/seek/duration/track authority. Existing UIA/GSMTC handoff rules remain responsible for retaking the real clock when available.

## Protected paths unchanged

- QQ healthy GSMTC veto, seek/hover protections, Text boundary clock, RangeV2 fuse and track-duration authority logic.
- NetEase native-log authority / track serial / stale-carry transition logic.
- KuGou Host V2 / RangeValue / rail authority and 21 golden methods.
- PyInstaller `.spec` and canonical PyInstaller command.

## Validation

`CHECK_PRECISION_LADDER_QQ_BACKGROUND_REPLAY.py` covers the precise quality ladder, classic ordinary-only retrieval, cache-mode separation, and QQ background display-only acceptance/rejection cases. The release builder invokes this gate before packaging.

Actual Windows runtime validation is still required for hidden/minimized QQ auto-next playback and the live NetEase `烂尾楼` cross-provider precise selection.
